
import time
import pathlib
import re

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt, cm, patches, ticker
from matplotlib.colors import LinearSegmentedColormap
import pysam

from triplix.core.header import TriplixHeader
from triplix.core import configurations
from triplix.core import concatemers
from triplix.core.triplets import TripletsContainer
from triplix.core.tri_alignments import TriAlignmentsContainer
from triplix._logging import get_logger

COMMAND_NAME = 'triplix.plot'
logger = get_logger(COMMAND_NAME)


def plot_virtual_hic(
        input_patterns,
        view_chrom, view_start, view_end,
        view_point,
        anchor_width=None,
        plot_names=('count_ABC',),
        mapping_quality=5,
        output_dir=None,
        output_name=None,
        plot_params=None,
):
    # prepare plot parameters
    parameters = {}
    for plot_name in plot_names:
        if plot_name.endswith('.enrichment'):
            parameters[plot_name] = {
                'clim_range': [-4, 4],
                'draw_values': False,
            }
        else:
            parameters[plot_name] = {
                'clim_prct': [20, 96],
                'draw_values': False,
            }
    # setting user-defined parameters
    for regex_name in plot_params:
        for plot_name in plot_names:
            if re.match(regex_name, plot_name):
                for key, value in plot_params[regex_name].items():
                    parameters[plot_name][key] = value

    # casting input parameters to proper type casting
    input_patterns = input_patterns.split(',')
    view_start = int(view_start)
    view_end = int(view_end)
    view_point = int(view_point)

    # collecting input files
    logger.debug(f'Collecting input files from {len(input_patterns)} given patterns:')
    input_files = []
    for pi, pattern in enumerate(input_patterns):
        logger.debug(f'Pattern #{pi + 1}: {pattern}')
        path = pathlib.Path(pattern).expanduser()
        input_files.extend(path.parent.glob(path.name))
    logger.debug(f'Found {len(input_files):d} input files:')
    for file_idx, file_path in enumerate(input_files):
        logger.debug(f'\t{file_idx + 1:2d}: {file_path}')
    assert len(input_files) > 0, 'At least a single input file is required for plotting'

    # define output directory and filename
    if output_dir is None:
        output_dir = input_files[0].parent
    if output_name is None:
        output_name = (
            f'virtual-hic.{view_chrom}'
            f'_{view_start:09,d}-{view_end:09,d}'
            f'.vp-{view_point:09,d}'
            f'.{input_files[0].name}.{plot_names[-1]}'
            f'.nf{len(input_files):d}.np{len(plot_names):d}'
            f'.pdf')
    output_path = pathlib.Path(output_dir).expanduser() / output_name
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # collecting metadata
    chrom_lengths = None
    for input_idx, input_path in enumerate(input_files):

        # collecting the header and anchor width if needed
        input_header = TriplixHeader(file_path=str(input_path))
        if input_header.anchor_width is not None:
            if anchor_width is None:
                anchor_width = input_header.anchor_width
            else:
                assert anchor_width == input_header.anchor_width, 'At least one file has an incompatible `anchor_width`'
        if input_header.chrom_lengths is not None:
            if chrom_lengths is None:
                chrom_lengths = input_header.chrom_lengths
            else:
                assert chrom_lengths == input_header.chrom_lengths, 'At least one file has an incompatible `chrom_length`'
    assert anchor_width is not None, '`anchor_width` should be defined, either in CLI arguments, or input files.'
    assert chrom_lengths is not None, '`chrom_lengths` should be defined in at least one input file.'
    anchor_width = int(anchor_width)

    # define the chunk area
    if view_start > chrom_lengths[view_chrom]:
        logger.info(f'The requested window ({view_start / 1e6:0.2f}-{view_end / 1e6:0.2f}mb) '
                    f'is outside of {view_chrom} (length={chrom_lengths[view_chrom] / 1e6:0.2f}mb). '
                    f'No processing is needed.')
        return
    assert view_start <= view_point < view_end, 'The viewpoint is out of the view area'
    logger.info(f'Area of interest is: '
                f'{view_chrom}:{view_start:0,d}-{view_end:0,d} | vp={view_point:0,d}. ')

    # define anchors
    anchor_edges = np.arange(view_start, view_end + anchor_width, anchor_width, dtype=int)
    vp_bdx = np.searchsorted(anchor_edges, view_point, side='right') - 1
    n_anchor = len(anchor_edges) - 1

    # collecting counts from each input file
    images = {col_name: np.full([n_anchor, n_anchor], fill_value=np.nan) for col_name in plot_names}
    for input_idx, input_path in enumerate(input_files):
        logger.info(f'{input_idx + 1:d}/{len(input_files):d}: Processing: {input_path}')

        # if the input is a BAM file
        if str(input_path).endswith('.bam'):

            # check file to be sorted and indexed
            if not pathlib.Path(str(input_path) + '.bai').is_file():
                raise FileNotFoundError(f'Missing index file. Please index the coord-sorted BAM file using `samtools index` command: {input_path}')
            bam_header = TriplixHeader(file_path=str(input_path))
            if bam_header.process_history.headers['HD']['SO'] != 'coordinate':
                raise ValueError(f'BAM files need to be "coordinate" sorted. Please sort using `samtools sort` command: {input_path}')

            # collect read ids
            logger.debug('\tCollecting "read_names" that contain the viewpoint ...')
            read_ids = set()
            with pysam.AlignmentFile(input_path, 'r', require_index=True) as bam_fid:
                alignment_iter = bam_fid.fetch(view_chrom, anchor_edges[vp_bdx], anchor_edges[vp_bdx + 1])  # start and stop denote 0-based, half-open intervals, i.e., [start, end).
                for aln_idx, aln in enumerate(alignment_iter):
                    if aln.mapping_quality >= mapping_quality:
                        read_ids.add(aln.query_name)
            logger.debug(f'\t{len(read_ids):,d} reads contain the viewpoint.')
            if len(read_ids) == 0:
                logger.warning(f'No read contains the viewpoint, ignoring: {input_path}')
                continue

            # collecting interactions
            logger.debug('\tCollecting interactions of the selected reads ...')
            alignments = []
            n_ignore = 0
            logger.log_time = time.time()
            with pysam.AlignmentFile(input_path, 'r', require_index=True) as bam_fid:
                alignment_iter = bam_fid.fetch(view_chrom, view_start, view_end)
                n_load = 0
                for aln_idx, aln in enumerate(alignment_iter):
                    if time.time() - logger.log_time > configurations.configs['log_interval']:
                        logger.debug(f'\t\tcurrently processing {aln_idx:d}th alignment')
                        logger.log_time = time.time()
                    if aln.query_name not in read_ids:
                        continue
                    if aln.mapping_quality < mapping_quality:
                        n_ignore += 1
                        continue
                    n_load += 1

                    alignment = dict(
                        id=aln.query_name,
                        chrom=aln.reference_name,
                        start=aln.reference_start,
                        end=aln.reference_end,
                        mapq=aln.mapping_quality,
                    )
                    alignments.append(alignment)
            logger.debug(f'\tIn total {n_load:d} alignments are collected, and {n_ignore:,d} are ignored.')

            # conversion to DataFrame
            alignments = pd.DataFrame(alignments)
            assert alignments['id'].isin(read_ids).all()
            assert np.isin(list(read_ids), alignments['id']).all()

            # identify the VP alignments
            # alignments['is_vp'] = False
            # is_vp = (
            #         (alignments['start'] < anchor_edges[vp_bdx + 1])
            #         & (alignments['end'] >= anchor_edges[vp_bdx])
            # )
            # assert np.array_equal(sorted(set(alignments.loc[is_vp, 'id'])),
            #                       sorted(set(alignments['id'])))
            # alignments.loc[is_vp, 'is_vp'] = True
            # alignments = alignments.sort_values(by=['id', 'is_vp', 'start'], ascending=[True, False, True]).reset_index(drop=True)
            # alignments = alignments[~is_vp].reset_index(drop=True)
            # logger.debug(f'\t{len(alignments):,d} alignments are left after viewpoint exclusion.')

            # sort, and map alignments to bins
            alignments = alignments.sort_values(by=['id', 'start']).reset_index(drop=True)
            alignments['start_bidx'] = np.searchsorted(anchor_edges, alignments['start'], side='right') - 1
            alignments['end_bidx'] = np.searchsorted(anchor_edges, alignments['end'], side='right') - 1

            # add alignments to the counts
            logger.debug('\tMapping alignments to bins')
            n_dup = 0
            seen_ids = dict()
            n_contact = 0
            alignment_grp = alignments.groupby(by='id', sort=False)
            for read_idx, (read_id, read) in enumerate(alignment_grp):
                n_frag = len(read)
                if n_frag < 3:
                    continue

                # store tri-alignments (ignoring the first viewpoint alignment)
                # assert read['is_vp'].iat[0]
                for fi in range(n_frag):
                    frg_i = read.iloc[fi]
                    for fj in range(fi + 1, n_frag):
                        frg_j = read.iloc[fj]
                        for fk in range(fj + 1, n_frag):
                            frg_k = read.iloc[fk]
                            # if np.abs(frg_j['start'] - frg_i['start']) < cli_args.min_dist:
                            #     continue
                            for ovl_i in range(frg_i['start_bidx'], frg_i['end_bidx'] + 1):
                                if not 0 <= ovl_i < n_anchor:
                                    continue
                                for ovl_j in range(frg_j['start_bidx'], frg_j['end_bidx'] + 1):
                                    if not 0 <= ovl_j < n_anchor:
                                        continue
                                    for ovl_k in range(frg_k['start_bidx'], frg_k['end_bidx'] + 1):
                                        if not 0 <= ovl_k < n_anchor:
                                            continue

                                        # assigning a pair id
                                        pair_id = list(sorted([ovl_i, ovl_j, ovl_k]))
                                        if not any(i == vp_bdx for i in pair_id):
                                            continue
                                        pair_id.pop(pair_id.index(vp_bdx))
                                        pair_id = tuple(pair_id)

                                        # ignore if the read has contributed to the current bin-triplet already
                                        if pair_id not in seen_ids:
                                            seen_ids[pair_id] = set()
                                        if read_id in seen_ids[pair_id]:
                                            n_dup += 1
                                            continue
                                        seen_ids[pair_id].add(read_id)

                                        # add the counts
                                        bdx_j, bdx_k = pair_id
                                        if np.isnan(images['count_ABC'][bdx_j, bdx_k]):
                                            images['count_ABC'][bdx_j, bdx_k] = 0
                                            images['count_ABC'][bdx_k, bdx_j] = 0
                                        images['count_ABC'][bdx_j, bdx_k] += 1
                                        if bdx_j != bdx_k:
                                            images['count_ABC'][bdx_k, bdx_j] += 1
                                        n_contact += 1

                                    # ###
                                    # if ovl_i == 1 and ovl_j == 20:
                                    #     print(read[['id', 'start', 'end', 'start_bidx', 'end_bidx']])
                                    #     print(images['count_ABC'][ovl_i, ovl_j])

            # seen_ids_collection[bam_fpath] = copy.deepcopy(seen_ids)
            logger.info(f'\t{n_contact:,d} contacts are stored, and {n_dup:,d} are ignored due to duplicity.')

        # tri-alignment input
        elif str(input_path).endswith('.tri-alignments.tsv.bgz'):
            logger.info(f'Loading tri-alignments from: {input_path}')
            tri_alignments_obj = TriAlignmentsContainer(trialn_path=input_path)

            # map tri-alignments to data cubes
            anchor_max_distance = anchor_edges[-1] - anchor_edges[0]
            counts = np.zeros([n_anchor, n_anchor, n_anchor], dtype=int)
            n_load = 0
            logger.log_time = 0
            for ai in range(n_anchor):
                if time.time() - logger.log_time > configurations.configs['log_interval']:
                    logger.log_time = time.time()
                    logger.info(f'\tcurrently at {anchor_edges[ai]:,d} ({ai:3d}/{n_anchor}) anchor, and loaded {n_load:,d} (unique) tri-alignments')
                counts[ai, :, :] = tri_alignments_obj.fetch_slice(
                    vp_chrom=view_chrom, vp_start=anchor_edges[ai], vp_end=anchor_edges[ai + 1] - 1,
                    anchor_edges=anchor_edges,
                    anchor_max_distance=anchor_max_distance,
                    mapping_quality=mapping_quality
                )
                n_load += np.sum(counts[ai, :, :])

            # make the counts symmetric
            logger.debug('Making the counts cube symmetric')
            for ai in range(n_anchor):
                for aj in range(ai, n_anchor):
                    for ak in range(aj, n_anchor):
                        counts[ai, ak, aj] = counts[ai, aj, ak]
                        counts[aj, ai, ak] = counts[ai, aj, ak]
                        counts[aj, ak, ai] = counts[ai, aj, ak]
                        counts[ak, ai, aj] = counts[ai, aj, ak]
                        counts[ak, aj, ai] = counts[ai, aj, ak]

            # calculate triplet properties
            cubes = {}
            for col_name in plot_names:
                cubes[col_name] = np.full([n_anchor, n_anchor, n_anchor], fill_value=np.nan)
                if col_name == 'count_ABC':
                    cubes[col_name] = counts.copy()
                else:
                    logger.warning(f'Estimation of {col_name} from tri-alignments is not implemented. This map will be all NaNs.')

            # collect data from the viewpoint slice
            for col_name in plot_names:
                has_value = np.isnan(images[col_name]) & ~ np.isnan(cubes[col_name][vp_bdx])
                images[col_name][has_value] = 0
                images[col_name][has_value] += cubes[col_name][vp_bdx][has_value]

        elif str(input_path).endswith('.triplets.h5'):
            logger.info(f'Loading triplets from: {input_path}')

            # prepare Triplets object
            triplets_obj = TripletsContainer(input_path)
            triplets = triplets_obj.fetch(
                chrom_a=view_chrom, start_a=anchor_edges[0], end_a=anchor_edges[-1] - 1,
                chrom_b=view_chrom, start_b=anchor_edges[0], end_b=anchor_edges[-1] - 1,
                chrom_c=view_chrom, start_c=anchor_edges[0], end_c=anchor_edges[-1] - 1,
                exclusive=True
            )

            # map triplets to data slices
            slice_maps = {}
            for col_name in plot_names:
                slice_maps[col_name] = triplets.to_slice(view_point=view_point, anchor_edges=anchor_edges, value_column=col_name)

            # collect data from the viewpoint slice
            for col_name in plot_names:
                has_value = np.isnan(images[col_name]) & ~ np.isnan(slice_maps[col_name])
                images[col_name][has_value] = 0
                images[col_name][has_value] += slice_maps[col_name][has_value]
        else:
            raise ValueError(f'Unknown file type: {input_path}')
    # n_load = np.nansum(image)
    # assert n_load > 0, 'No contacts were found in this area.'

    # filter NaN values
    if 'count_ABC' in images:
        is_nan = np.isnan(images['count_ABC'])
        images['count_ABC'][is_nan] = 0

    # prepare a figure
    ext_bnd = [view_start, view_end]
    # n_row = int(np.ceil(len(plot_names) / 4))
    # n_col = min(len(plot_names), 4)
    n_row = 1
    n_col = len(plot_names)
    plt.close('all')
    fig_h, axes = plt.subplots(nrows=n_row, ncols=n_col, figsize=(n_col * 10, n_row * 8 + 1))
    if hasattr(axes, '__len__'):
        axes = axes.flatten()
    else:
        axes = [axes]
    for pi, col_name in enumerate(plot_names):

        # prepare a colormap
        if col_name.endswith('.enrichment'):
            axes[pi].cmap = LinearSegmentedColormap.from_list('bwwr', ['#0000ff', '#ffffff', '#ff0000'])
            axes[pi].cmap.set_over(color='#700000', alpha=1.0)
            axes[pi].cmap.set_under(color='#000070', alpha=1.0)
            axes[pi].clim = parameters[col_name]['clim_range']
        else:
            axes[pi].cmap = cm.get_cmap('hot_r', 20)
            axes[pi].cmap.set_under(color='#ffffff', alpha=1.0)
            # cmap.set_over(color='#000055', alpha=1.0)
        axes[pi].cmap.set_bad(color='#b2b2a3', alpha=0.5)

        # draw the image
        axes[pi].img_h = axes[pi].imshow(
            images[col_name],
            interpolation='nearest',
            cmap=axes[pi].cmap, aspect='auto',
            extent=ext_bnd + ext_bnd[::-1],
        )

        axes[pi].cb_h = plt.colorbar(axes[pi].img_h, ax=axes[pi], fraction=0.025, pad=0.03, extend='both')
        # axes[pi].cb_h.ax.tick_params(labelsize=10)

        # set color ranges
        if 'clim_range' in parameters[col_name]:
            axes[pi].clim = parameters[col_name]['clim_range']
        elif 'clim_prct' in parameters[col_name]:
            prct_range = parameters[col_name]['clim_prct']
            axes[pi].clim = np.nanpercentile(images[col_name], prct_range)
        else:
            raise ValueError('Can not determine the `clim` variable range.')
        axes[pi].img_h.set_clim(axes[pi].clim)

        # add viewpoint bars
        axes[pi].add_patch(patches.Rectangle((ext_bnd[0], view_point), ext_bnd[1] - ext_bnd[0], anchor_width,
                                             linewidth=0, edgecolor='None', facecolor='#66a96c', alpha=1.0))
        axes[pi].add_patch(patches.Rectangle((view_point, ext_bnd[0]), anchor_width, ext_bnd[1] - ext_bnd[0],
                                             linewidth=0, edgecolor='None', facecolor='#66a96c', alpha=1.0))

        x_tick_pos = np.unique(np.linspace(view_start, view_end, 25, dtype=int))
        axes[pi].set_xticks(x_tick_pos)
        axes[pi].set_yticks(x_tick_pos)
        axes[pi].xaxis.set_tick_params(rotation=60)
        # axes[pi].xaxis.set_major_locator(ticker.MaxNLocator(nbins=17, integer=False))
        # axes[pi].yaxis.set_major_locator(ticker.MaxNLocator(nbins=17, integer=False))
        axes[pi].xaxis.set_major_formatter(lambda v, _: '{:0.2f}'.format(v / 1e6))
        axes[pi].yaxis.set_major_formatter(lambda v, _: '{:0.2f}'.format(v / 1e6))
        # axes[pi].xaxis.set_tick_params(labelsize=10)
        # axes[pi].yaxis.set_tick_params(labelsize=10)

        axes[pi].set_title(f'{col_name}\nsum={np.nansum(images[col_name]):0.1f}')

        # drawing the values over map
        if parameters[col_name].get('draw_values', False):
            norm = plt.Normalize(*axes[pi].clim)
            for aj in range(n_anchor):
                for ak in range(n_anchor):
                    value = images[col_name][aj, ak]
                    if np.round(value, decimals=1) == 0:
                        continue

                    # define the color from luminance
                    # source: https://stackoverflow.com/questions/596216/formula-to-determine-perceived-brightness-of-rgb-color
                    color_rgb = axes[pi].cmap(norm(value))
                    luminance = color_rgb[0] * 0.2126 + color_rgb[1] * 0.7152 + color_rgb[2] * 0.0722
                    if luminance < 0.549019:  # 0.549019 = 140 / 255
                        text_color = '#FFFFFF'
                    else:
                        text_color = '#000000'

                    # plotting the value
                    axes[pi].text(
                        anchor_edges[ak] + anchor_width // 2,
                        anchor_edges[aj] + anchor_width // 2,
                        f'{value:0.1f}', color=text_color, fontsize=1, zorder=100, va='center', ha='center',
                    )
        
        # adding annotations
        if 'annotations' in parameters[col_name]:
            logger.debug(f'Drawing annotations on: {col_name} ...')
            ant_color = '#000000'  # '#F4FF0A'
            for ant_idx, (b_beg, b_end, c_beg, c_end) in enumerate(parameters[col_name]['annotations']):
                axes[pi].add_patch(patches.Rectangle((c_beg, b_beg), c_end - c_beg, b_end - b_beg, linewidth=3, facecolor='none', edgecolor=ant_color, alpha=0.8))

    plt.suptitle(f'{input_files[0].name}, #files used: {len(input_files)}\n'
                 f'{view_chrom}:{view_start / 1e6:0,.3f}-{view_end / 1e6:0,.3f}mb, viewpoint={view_point / 1e6:0,.3f}mb\n'
                 f'anchor width={anchor_width / 1e3:0.0f}k; mapping quality={mapping_quality}',
                 fontweight='normal')  # y=1 + 0.15 / (n_row * 3)
    plt.subplots_adjust(top=1.0 - 0.17 / n_row, wspace=0.2, hspace=0.2)  # , top=0.8
    # plt.show()

    # logger_fonttools = logging.getLogger('fontTools.subset')
    # logger_fonttools = logging.getLogger('matplotlib')
    # loglevel_prev = logger_fonttools.level
    # logger_fonttools.setLevel(logging.WARNING)
    plt.savefig(output_path, bbox_inches='tight')
    # logger_fonttools.setLevel(loglevel_prev)
    plt.close()
    logger.info(f'Virtual-HiC plot is stored in: {output_path}')


def plot_hic(
        input_patterns,
        view_chrom, view_start, view_end,
        anchor_width=None,
        plot_names=('count_AB',),
        mapping_quality=5,
        output_dir=None,
        output_name=None,
        plot_params=None,
):
    # casting input parameters to proper type casting
    if plot_params is None:
        plot_params = {}
    input_patterns = input_patterns.split(',')
    view_start = int(view_start)
    view_end = int(view_end)

    # collecting input files
    logger.debug(f'Collecting input files from {len(input_patterns)} given patterns:')
    input_files = []
    for pi, pattern in enumerate(input_patterns):
        logger.debug(f'Pattern #{pi + 1}: {pattern}')
        path = pathlib.Path(pattern).expanduser()
        input_files.extend(path.parent.glob(path.name))
    logger.debug(f'Found {len(input_files):d} input files:')
    for file_idx, file_path in enumerate(input_files):
        logger.debug(f'\t{file_idx + 1:2d}: {file_path}')
    assert len(input_files) > 0, 'At least a single input file is required for plotting'

    # define output directory and filename
    if output_dir is None:
        output_dir = input_files[0].parent
    if output_name is None:
        output_name = f'hic.{view_chrom}_{view_start:09,d}-{view_end:09,d}.{input_files[0].stem}.pdf'
    output_path = pathlib.Path(output_dir).expanduser() / output_name
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # collecting metadata
    chrom_lengths = None
    for input_idx, input_path in enumerate(input_files):

        # collecting the header and anchor width if needed
        input_header = TriplixHeader(file_path=str(input_path))
        if input_header.anchor_width is not None:
            if anchor_width is None:
                anchor_width = input_header.anchor_width
            else:
                assert anchor_width == input_header.anchor_width, 'At least one file has an incompatible `anchor_width`'
        if input_header.chrom_lengths is not None:
            if chrom_lengths is None:
                chrom_lengths = input_header.chrom_lengths
            else:
                assert chrom_lengths == input_header.chrom_lengths, 'At least one file has an incompatible `chrom_length`'
    assert anchor_width is not None, '`anchor_width` should be defined, either in CLI arguments, or input files.'
    assert chrom_lengths is not None, '`chrom_lengths` should be defined in at least one input file.'
    anchor_width = int(anchor_width)

    # define the chunk area
    if view_start > chrom_lengths[view_chrom]:
        logger.info(f'The requested window ({view_start / 1e6:0.2f}-{view_end / 1e6:0.2f}mb) '
                    f'is outside of {view_chrom} (length={chrom_lengths[view_chrom] / 1e6:0.2f}mb). '
                    f'No processing is needed.')
        return
    logger.info(f'Area of interest is: {view_chrom}:{view_start:0,d}-{view_end:0,d}')

    # define anchors
    anchor_edges = np.arange(view_start, view_end + anchor_width, anchor_width, dtype=int)
    n_anchor = len(anchor_edges) - 1

    # collecting counts from each input file
    images = {col_name: np.full([n_anchor, n_anchor], fill_value=np.nan) for col_name in plot_names}
    for input_idx, input_path in enumerate(input_files):
        logger.info(f'{input_idx + 1:d}/{len(input_files):d}: Processing: {input_path}')

        if input_path.suffix in ['.bam']:

            # check file to be sorted and indexed
            if not pathlib.Path(str(input_path) + '.bai').is_file():
                raise FileNotFoundError(f'Missing index file. Please index the coord-sorted BAM file using `samtools index` command: {input_path}')
            bam_header = TriplixHeader(file_path=str(input_path))
            if bam_header.process_history.headers['HD']['SO'] != 'coordinate':
                raise ValueError(f'Input BAM file need to be "coordinate" sorted. Please sort using `samtools sort` command: {input_path}')

            # collecting interactions
            alignments = []
            n_ignore = 0
            with pysam.AlignmentFile(input_path, 'r', require_index=True) as bam_fid:
                alignment_iter = bam_fid.fetch(view_chrom, view_start, view_end)
                n_load = 0
                for aln_idx, aln in enumerate(alignment_iter):
                    if aln_idx % 1e6 == 0:
                        logger.debug(f'\t\tcurrently processing {aln_idx:d}th alignment')
                    if aln.mapping_quality < mapping_quality:
                        n_ignore += 1
                        continue
                    n_load += 1
                    alignment = dict(
                        id=aln.query_name,
                        chrom=aln.reference_name,
                        start=aln.reference_start,
                        end=aln.reference_end,
                        mapq=aln.mapping_quality,
                    )
                    alignments.append(alignment)
            logger.debug(f'\tIn total {n_load:,d} alignments are collected, and {n_ignore:,d} are ignored.')
            if n_load == 0:
                logger.warning(f'No alignments were found in this area, ignoring: {input_path}')
                continue

            # form a dataframe from alignments
            alignments = pd.DataFrame(alignments)
            alignments = alignments.sort_values(by=['id', 'start']).reset_index(drop=True)

            # excluding reads with #alignments < 2
            is_singleton = alignments.groupby(by='id', sort=False)['id'].transform('size') < 2
            alignments = alignments.loc[~is_singleton].reset_index(drop=True)
            logger.debug(f'\t{len(alignments):,d} alignments, and {len(alignments["id"].unique()):,d} reads are left after #alignment>1 filter')
            del is_singleton

            # map alignments to bins
            alignments['start_bidx'] = np.searchsorted(anchor_edges, alignments['start'], side='right') - 1
            alignments['end_bidx'] = np.searchsorted(anchor_edges, alignments['end'], side='right') - 1

            # add alignments to the counts
            n_dup = 0
            seen_ids = dict()
            n_contact = 0
            for read_idx, (read_id, read) in enumerate(alignments.groupby(by='id', sort=False)):
                n_frag = len(read)
                if n_frag < 1:
                    continue

                # store pairwise contacts
                for fi in range(n_frag):
                    for fj in range(fi + 1, n_frag):
                        frg_i = read.iloc[fi]
                        frg_j = read.iloc[fj]
                        # if np.abs(frg_j['start'] - frg_i['start']) < cli_args.min_dist:
                        #     continue

                        for ovl_i in range(frg_i['start_bidx'], frg_i['end_bidx'] + 1):
                            if not 0 <= ovl_i < n_anchor:
                                continue

                            for ovl_j in range(frg_j['start_bidx'], frg_j['end_bidx'] + 1):
                                if not 0 <= ovl_j < n_anchor:
                                    continue

                                pair_id = (ovl_i, ovl_j)
                                if pair_id not in seen_ids:
                                    seen_ids[pair_id] = set()
                                    if np.isnan(images['count_AB'][ovl_i, ovl_j]):
                                        images['count_AB'][ovl_i, ovl_j] = 0
                                        images['count_AB'][ovl_j, ovl_i] = 0

                                # ignore, if the read has already contributed to the current triplet
                                if read_id in seen_ids[pair_id]:
                                    n_dup += 1
                                    continue
                                seen_ids[pair_id].add(read_id)

                                images['count_AB'][ovl_i, ovl_j] += 1
                                images['count_AB'][ovl_j, ovl_i] += 1
                                n_contact += 1
            # seen_ids_collection[bam_fpath] = copy.deepcopy(seen_ids)
            logger.info(f'\t{n_contact:,d} contacts are stored, and {n_dup:,d} are ignored due to duplicity.')

        else:
            raise ValueError(f'Unknown file type: {input_path}')
    # n_load = np.nansum(image)
    # assert n_load > 0, 'No contacts were found in this area.'

    # prepare a figure
    # LinearSegmentedColormap.from_list('bwwr', ['#0000ff', '#ffffff', '#ff0000'])
    cmap = cm.get_cmap('hot_r', 20)
    cmap.set_bad(color='#b2b2a3', alpha=0.5)
    cmap.set_under(color='#ffffff', alpha=1.0)
    # cmap.set_over(color='#000055', alpha=1.0)
    ext_bnd = [view_start, view_end]
    n_row = int(np.ceil(len(plot_names) / 4))
    n_col = min(len(plot_names), 4)
    plt.close('all')
    fig_h, axes = plt.subplots(nrows=n_row, ncols=n_col, figsize=(n_col * 10, n_row * 8 + 1))
    axes = axes.flatten()
    for pi, col_name in enumerate(plot_names):
        axes[pi].img_h = axes[pi].imshow(
            images[col_name],
            interpolation='nearest',
            cmap=cmap, aspect='auto',
            extent=ext_bnd + [view_end, view_start],
        )

        axes[pi].cb_h = plt.colorbar(axes[pi].img_h, ax=axes[pi], fraction=0.025, pad=0.03, extend='both')
        # axes[pi].cb_h.ax.tick_params(labelsize=10)

        if col_name in plot_params and 'clim_range' in plot_params[col_name]:
            c_lim = [float(value) for value in plot_params[col_name]['clim_range'].split(',')]
        elif col_name in plot_params and 'clim_prct' in plot_params[col_name]:
            c_lim_prct = [float(value) for value in plot_params[col_name]['clim_prct'].split(',')]
            c_lim = [np.nanpercentile(images[col_name], c_lim_prct[0]), np.nanpercentile(images[col_name], c_lim_prct[1])]
        else:
            c_lim = [np.nanpercentile(images[col_name], 20), np.nanpercentile(images[col_name], 96)]
        axes[pi].img_h.set_clim(c_lim)

        x_tick_pos = np.unique(np.linspace(view_start, view_end, 25, dtype=int))
        axes[pi].set_xticks(x_tick_pos)
        axes[pi].set_yticks(x_tick_pos)
        axes[pi].xaxis.set_tick_params(rotation=60)
        axes[pi].xaxis.set_major_formatter(lambda v, _: '{:0.2f}'.format(v / 1e6))
        axes[pi].yaxis.set_major_formatter(lambda v, _: '{:0.2f}'.format(v / 1e6))

        axes[pi].set_title(f'{col_name}\nsum={np.nansum(images[col_name])}')

    plt.suptitle(f'{input_files[0].name}, #files used: {len(input_files)}\n'
                 f'{view_chrom}:{view_start / 1e6:0,.3f}-{view_end / 1e6:0,.3f}mb\n'
                 f'anchor width={anchor_width / 1e3:0.0f}k',
                 fontweight='normal')  # y=1 + 0.15 / (n_row * 3)
    plt.subplots_adjust(top=1.0 - 0.17 / n_row, wspace=0.2, hspace=0.2)  # , top=0.8
    # plt.show()

    # logger_fonttools = logging.getLogger('fontTools.subset')
    # loglevel_prev = logger_fonttools.level
    # logger_fonttools.setLevel(logging.WARNING)
    plt.savefig(output_path, bbox_inches='tight')
    # logger_fonttools.setLevel(loglevel_prev)
    plt.close()
    logger.info(f'Virtual-HiC plot is stored in: {output_path}')


def plot_processing_history(input_path, output_dir=None, output_name=None, **kwargs):
    input_path = pathlib.Path(input_path).expanduser()
    header = TriplixHeader(file_path=input_path)

    # prepare the output path
    if output_dir is None:
        output_dir = input_path.parent
    if output_name is None:
        output_name = input_path.stem + '.processing-history.pdf'
    output_path = pathlib.Path(output_dir).expanduser() / output_name
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.is_file():
        output_path.unlink()

    header.process_history.visualize(output_path=output_path, **kwargs)


def plot_read_length_histogram(concatemers_path, output_dir=None, output_name=None):

    # prepare paths
    input_path = pathlib.Path(concatemers_path).expanduser()
    if output_dir is None:
        output_dir = input_path.parent
    if output_name is None:
        output_name = 'read-length.' + input_path.stem + '.pdf'
    output_path = pathlib.Path(output_dir).expanduser() / output_name
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # prepare the container
    cctm_container = concatemers.ConcatemersContainer(input_path)
    concatemers_iter = cctm_container.iter(return_length=True)

    # define bin edges
    max_length = 10e3
    bin_edges = np.hstack([np.linspace(0, max_length, 101, dtype=int), np.inf])
    bin_width = bin_edges[1] - bin_edges[0]
    n_bin = len(bin_edges) - 1
    counts = np.zeros(n_bin, dtype=int)

    # iterate over concatemers
    logger.log_time = time.time()
    n_concatemer = cctm_container.h5_file['/reads/name'].shape[0]
    logger.info(f'Iterating over {n_concatemer:,d} concatemers in: {concatemers_path}')
    n_load = 0
    for cctm_idx, concatemer in enumerate(concatemers_iter):
        n_load += 1
        if time.time() - logger.log_time > configurations.configs['log_interval']:
            logger.log_time = time.time()
            logger.info(f'\t{n_load:,d}/{n_concatemer:,d} concatemers are processed. ')

        # collect read length
        bin_idx = np.searchsorted(bin_edges, concatemer['read_length'], side='right') - 1
        counts[bin_idx] += 1

    # prepare a figure
    plt.close('all')
    fig_h = plt.figure(figsize=(16, 5))
    ax = plt.gca()

    ax.bar(bin_edges[:-1], counts, width=bin_width * 0.9, color='#2f1ee6', align='edge')

    ax.xaxis.set_major_locator(ticker.MaxNLocator(nbins=23, integer=True))
    ax.yaxis.set_major_locator(ticker.MaxNLocator(nbins=10, integer=True))
    ax.xaxis.set_major_formatter(lambda v, _: '{:0,.0f}'.format(v))
    ax.yaxis.set_major_formatter(lambda v, _: '{:0,.0f}'.format(v))
    ax.set_xlim([0, max_length * 1.01])
    ax.set_xlabel('Read length (bases)')
    ax.set_ylabel('Number of reads')

    ax.set_title(
        f'Read length distribution:\n'
        f'{input_path.name}\n'
        f'#concatemers={n_load:,d}',
    )
    # plt.show()

    # logger_fonttools = logging.getLogger('fontTools.subset')
    # loglevel_prev = logger_fonttools.level
    # logger_fonttools.setLevel(logging.WARNING)
    plt.savefig(output_path, bbox_inches='tight')
    # logger_fonttools.setLevel(loglevel_prev)
    plt.close()
    logger.info(f'Read length histogram is stored in: {output_path}')


def plot_alignment_length_histogram(
        concatemers_path,
        output_dir=None, output_name=None,
        mapping_quality=1, max_length=3e3,
):
    max_length = int(max_length)

    # prepare paths
    input_path = pathlib.Path(concatemers_path).expanduser()
    if output_dir is None:
        output_dir = input_path.parent
    if output_name is None:
        output_name = 'alignment-length.' + input_path.stem + '.pdf'
    output_path = pathlib.Path(output_dir).expanduser() / output_name
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # prepare the container
    cctm_container = concatemers.ConcatemersContainer(input_path)
    concatemers_iter = cctm_container.iter(return_length=True)

    # define bin edges
    bin_edges = np.hstack([np.linspace(0, max_length, 101, dtype=int), np.inf])
    bin_width = bin_edges[1] - bin_edges[0]
    n_bin = len(bin_edges) - 1
    counts = np.zeros(n_bin, dtype=int)

    # iterate over concatemers
    logger.log_time = time.time()
    n_concatemer = cctm_container.h5_file['/reads/name'].shape[0]
    logger.info(f'Iterating over {n_concatemer:,d} concatemers in: {concatemers_path}')
    n_load = 0
    n_alignments = 0
    for cctm_idx, concatemer in enumerate(concatemers_iter):
        n_load += 1
        if time.time() - logger.log_time > configurations.configs['log_interval']:
            logger.log_time = time.time()
            logger.info(f'\t{n_load:,d}/{n_concatemer:,d} concatemers are processed. ')

        # collect alignment lengths
        aln_lengths = concatemer['end'] - concatemer['start']
        bin_idxs = np.searchsorted(bin_edges, aln_lengths, side='right') - 1
        for aln_idx, bin_idx in enumerate(bin_idxs):
            if concatemer['map_quality'][aln_idx] < mapping_quality:
                continue
            n_alignments += 1
            counts[bin_idx] += 1

    # prepare a figure
    plt.close('all')
    fig_h = plt.figure(figsize=(16, 5))
    ax = plt.gca()

    ax.bar(bin_edges[:-1], counts, width=bin_width * 0.9, color='#2f1ee6', align='edge')

    ax.xaxis.set_major_locator(ticker.MaxNLocator(nbins=23, integer=True))
    ax.yaxis.set_major_locator(ticker.MaxNLocator(nbins=10, integer=True))
    ax.xaxis.set_major_formatter(lambda v, _: '{:0,.0f}'.format(v))
    ax.yaxis.set_major_formatter(lambda v, _: '{:0,.0f}'.format(v))
    ax.set_xlim([0, max_length * 1.01])
    ax.set_xlabel('Alignment length (bases)')
    ax.set_ylabel('Number of alignments')

    ax.set_title(
        f'Alignment length distribution:\n'
        f'{input_path.name}\n'
        f'#concatemers={n_load:,d}; #alignments={n_alignments:,d}; mapping_quality={mapping_quality:d}',
    )
    # plt.show()

    # logger_fonttools = logging.getLogger('fontTools.subset')
    # loglevel_prev = logger_fonttools.level
    # logger_fonttools.setLevel(logging.WARNING)
    plt.savefig(output_path, bbox_inches='tight')
    # logger_fonttools.setLevel(loglevel_prev)
    plt.close()
    logger.info(f'Alignment length histogram is stored in: {output_path}')

