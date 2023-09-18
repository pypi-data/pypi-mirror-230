import logging
import argparse
import re
import json

import numpy as np

from triplix.core import concatemers
from triplix.core import tri_alignment, triplet
from triplix.core import stat
from triplix.core import plot
from triplix._logging import get_logger

logger = get_logger(__name__)


def cli_concatemers(cli_args):
    exporter = concatemers.ExporterHDF5(
        bam_path=cli_args.input,
        assembly=cli_args.assembly,
        output_dir=cli_args.output_dir,
        output_name=cli_args.output_name,
        assume_sorted=cli_args.assume_sorted,
        cell_type=cli_args.cell_type,
        assay_name=cli_args.assay_name,
        experiment_name=cli_args.experiment_name,
    )
    exporter.initialize_hdf5()
    exporter.store_concatemers()


def cli_tri_alignments(cli_args):
    extractor = tri_alignment.extract.TriAlignmentExtractor(
        concatemers_path=cli_args.input,
        output_dir=cli_args.output_dir,
        output_name=cli_args.output_name,
    )
    extractor.extract_tri_alignments()


def cli_sort(cli_args):
    sorter = tri_alignment.sort.TriAlignmentSorter(
        trialign_path=cli_args.input,
        output_dir=cli_args.output_dir,
        output_name=cli_args.output_name,
    )
    sorter.sort_tri_alignments(n_thread=cli_args.threads,
                               memory=cli_args.memory)


def cli_merge(cli_args):
    if cli_args.metadata is None:
        metadata = {}
    else:
        metadata = dict(param.split(':') for param in cli_args.metadata.split(','))

    merger = tri_alignment.merge.TripletMerger(
        input_patterns=cli_args.input,
        output_dir=cli_args.output_dir,
        output_name=cli_args.output_name,
        concatenate_only=cli_args.concatenate,
        check_coverage=cli_args.check_coverage,
        sort_by=cli_args.sort_by,
        metadata=metadata,
    )
    merger.merge_triplets(n_thread=cli_args.threads,
                          memory=cli_args.memory,
                          ignore_headers=cli_args.ignore_samheaders)


def cli_index(cli_args):
    indexer = tri_alignment.index.TripletIndexer(
        triplet_path=cli_args.input,
    )
    indexer.index()


def cli_bin(cli_args):
    binner = triplet.bin.TriAlignmentBinner(
        input_path=cli_args.input,
        anchor_width=int(cli_args.anchor_width),
        anchor_max_distance=int(cli_args.anchor_max_distance),
        output_dir=cli_args.output_dir,
        output_name=cli_args.output_name,
    )
    binner.bin(
        chunk_chrom=cli_args.chunk_chrom,
        chunk_start=cli_args.chunk_start,
        chunk_end=cli_args.chunk_end,
        mapping_quality=cli_args.mapping_quality,
    )


def cli_transform(cli_args):
    # process transform's parameters
    params = json.loads(cli_args.transform_params)

    if cli_args.transform_name == 'Gaussian':

        smoother = triplet.transform.GaussianSmoother(
            triplet_path=cli_args.input,
        )
        smoother.smooth(
            chunk_chrom=cli_args.chunk_chrom,
            chunk_start=cli_args.chunk_start,
            chunk_end=cli_args.chunk_end,
            kernel_width=params['kernel_width'],
            kernel_scale=params['kernel_scale'],
            min_distance=int(cli_args.min_distance),
            max_distance=int(cli_args.max_distance),
            label=cli_args.transform_label,
        )
    else:
        raise ValueError(f'Unknown transformation: {cli_args.transform_name}')


def cli_kdtree(cli_args):
    chroms = cli_args.chroms
    if chroms is not None:
        chroms = chroms.split(',')

    nei_finder = triplet.kdtree.NeighborFinder(
        triplet_path=cli_args.input,
    )
    nei_finder.find_neighbors(
        factors_info=cli_args.factors,
        target=cli_args.target,
        chroms=chroms,
        output_dir=cli_args.output_dir,
        output_name=cli_args.output_name,
        n_samples=cli_args.n_samples,
    )


def cli_enrichment(cli_args):
    enrich_estimator = triplet.enrichment.EnrichmentEstimator(
        triplet_path=cli_args.input,
        kdtree_path=cli_args.kdtree,
    )
    enrich_estimator.estimate_enrichments(
        chunk_chrom=cli_args.chunk_chrom,
        chunk_start=cli_args.chunk_start,
        chunk_end=cli_args.chunk_end,
        n_neighbors=cli_args.n_neighbors,
        view_point=cli_args.view_point,
    )


def cli_plot_virtual_hic(cli_args):
    # process plot params
    if cli_args.plot_params is None:
        plot_params = {}
    else:
        plot_params = json.loads(cli_args.plot_params)

    # plot_params = {}
    # if cli_args.params is not None:
    #     for param_str in cli_args.params.split('|'):
    #         col_name, param_name, param_value = re.split(r'[:=]', param_str)
    #         if col_name not in plot_params:
    #             plot_params[col_name] = {}
    #         plot_params[col_name][param_name] = param_value

    # if param_name in ['clim_range']:
    #     plot_params[col_name][param_name] = [float(value) for value in param_value.split(',')]
    #     plot_params[col_name][param_name] = param_value
    # else:
    #     plot_params[col_name][param_name] = param_value

    plot.plot_virtual_hic(
        input_patterns=cli_args.input,
        view_chrom=cli_args.view_chrom,
        view_start=cli_args.view_start,
        view_end=cli_args.view_end,
        view_point=cli_args.view_point,
        anchor_width=cli_args.anchor_width,
        plot_names=cli_args.columns.split(','),
        mapping_quality=cli_args.mapping_quality,
        output_dir=cli_args.output_dir,
        output_name=cli_args.output_name,
        plot_params=plot_params,
    )


def cli_plot_hic(cli_args):
    # process plot params
    plot_params = {}
    if cli_args.params is not None:
        for param_str in cli_args.params.split('|'):
            col_name, param_name, param_value = re.split(r'[:=]', param_str)
            if col_name not in plot_params:
                plot_params[col_name] = {}
            if param_name in ['clim_range']:
                plot_params[col_name][param_name] = [float(value) for value in param_value.split(',')]
            else:
                plot_params[col_name][param_name] = param_value

    plot.plot_hic(
        input_patterns=cli_args.input,
        view_chrom=cli_args.view_chrom,
        view_start=cli_args.view_start,
        view_end=cli_args.view_end,
        anchor_width=cli_args.anchor_width,
        plot_names=cli_args.columns.split(','),
        mapping_quality=cli_args.mapping_quality,
        output_dir=cli_args.output_dir,
        output_name=cli_args.output_name,
        plot_params=plot_params,
    )


def cli_plot_processing_history(cli_args):
    # set igraph parameters
    kwargs = {}
    if cli_args.igraph_params is not None:
        for param in cli_args.igraph_params.split(','):
            key, value = param.split(':')
            if key == 'figsize':
                kwargs[key] = [float(field) for field in value.split('-')]
            else:
                kwargs[key] = value
    kwargs['title'] = kwargs.get('title', f'{cli_args.input}')

    plot.plot_processing_history(
        input_path=cli_args.input,
        output_dir=cli_args.output_dir,
        output_name=cli_args.output_name,
        **kwargs,
    )


def cli_plot_read_length_histogram(cli_args):
    plot.plot_read_length_histogram(
        concatemers_path=cli_args.input,
        output_dir=cli_args.output_dir,
        output_name=cli_args.output_name,
    )


def cli_plot_alignment_length_histogram(cli_args):
    plot.plot_alignment_length_histogram(
        concatemers_path=cli_args.input,
        output_dir=cli_args.output_dir,
        output_name=cli_args.output_name,
        mapping_quality=cli_args.mapping_quality,
        max_length=cli_args.max_length,
    )


def cli_stat_decay(cli_args):
    if cli_args.analysis == 'decay':
        stat.collect_contact_decay_stats(
            concatemer_path=cli_args.input,
            output_dir=cli_args.output_dir,
            output_name=cli_args.output_name,
        )
    else:
        raise ValueError(f'Unknown stat: {cli_args.analysis}')


def define_cli_arguments():
    """Generates command line arguments
    """
    parser_main = argparse.ArgumentParser(prog='triplix', add_help=False)
    commands = parser_main.add_subparsers(
        title='required commands are',
        dest='command',
        # help='Description:'
    )
    parser_main.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS, help='Show this help message and exit.')
    parser_main.add_argument('--debug', action='store_true', help='Activate the debug mode.')
    parser_main.add_argument('--log_level', type=int, default=logging.INFO, help='Log level. An integer in [0, 50] interval. With larger values Triplix will be more conservative in printing messages (default: %(default)s)')

    #########################################
    # forming concatemers
    parser_concatemers = commands.add_parser('concatemers', help='Parse input BAM file and extract Concatemers')
    optional = parser_concatemers._action_groups.pop()
    required = parser_concatemers.add_argument_group('required arguments')
    required.add_argument('--input', required=True, metavar='<PATH>', help='Path to the input BAM file. The BAM file should be sorted by `read name` (i.e., using `samtools sort -n`)')
    optional.add_argument('--assembly', default='unknown', metavar='<STRING>', help='Name of the assembly (or genome) such as `hg19`, `hg38`, `mm10`, etc. (default: %(default)s)')
    optional.add_argument('--output_dir', default='./concatemers/', metavar='<PATH>',
                          help='Output directory where the output Concatemers file (.concatemers.h5) will be stored (default: %(default)s)')
    optional.add_argument('--output_name', default=None, metavar='<FILENAME>',
                          help='Output Concatemers file name. If not provided, the `experiment_name` is used with an added `.concatemers.h5` extension')
    optional.add_argument('--assume_sorted', action='store_true', help='Disables the name-sort check and assumes that the input BAM file is name sorted (default: %(default)s)')
    optional.add_argument('--cell_type', default='unknown', metavar='<STRING>', help='Name of the cell-type that is used to produce the current experiment (default: %(default)s)')
    optional.add_argument('--assay_name', default='unknown', metavar='<STRING>', help='Name of the assay that is used to produce the current experiment (default: %(default)s)')
    optional.add_argument('--experiment_name', default=None, metavar='<STRING>', help='A name for the current experiment. If not provided, the input BAM filename will be used as the `--experiment_name` instead.')
    parser_concatemers._action_groups.append(optional)
    parser_concatemers.set_defaults(func=cli_concatemers)

    #########################################
    # extracting tri-alignments
    parser_tri_alignments = commands.add_parser('tri_alignments', help='Process a Concatemers file (.concatemers.h5) and extract Tri-alignments from it')
    parser_tri_alignments.add_argument('--input', required=True, metavar='<PATH>', help='Path to input Concatemers file (e.g. `*.concatemers.h5`)')
    parser_tri_alignments.add_argument('--output_dir', default='./tri-alignments/', metavar='<PATH>',
                                       help='Output directory where the extracted Tri-alignments will be stored (default: %(default)s)')
    parser_tri_alignments.add_argument('--output_name', default=None, metavar='<FILENAME>',
                                       help='Output file name for the extracted Tri-alignments. If not provided, the output is stored using the input Concatemers file name, with a `.tri-alignments.tsv.bgz` extension')
    parser_tri_alignments.set_defaults(func=cli_tri_alignments)

    #########################################
    # sorting tri-alignments
    parser_sort = commands.add_parser('sort', help='Sort a Tri-alignments file according to the chromosomal positions of its Tri-alignments anchors.')
    parser_sort.add_argument('--input', required=True, metavar='<PATH>', help='Path to Tri-alignments file (e.g. `*.tri-alignments.tsv.bgz`)')
    parser_sort.add_argument('--output_dir', default='./tri-alignments_sorted', metavar='<PATH>',
                             help='Output directory where the sorted Tri-alignments file will be stored (default: %(default)s)')
    parser_sort.add_argument('--output_name', default=None, metavar='<FILENAME>',
                             help='Output name for the sorted Tri-alignments file. If not provided, the output is stored using the input Tri-alignments filename, with a `.sorted.tri-alignments.tsv.bgz` extension')
    parser_sort.add_argument('--memory', default='2G', metavar='<FLOAT>G', help='Amount of memory (in Gigabyte, or another supported size unit) that can be used by `sort` program (default: "%(default)s")')
    parser_sort.add_argument('--threads', default=1, type=int, metavar='<INTEGER>', help='Number of threads that can be used by `sort` program (default: "%(default)s")')
    parser_sort.set_defaults(func=cli_sort)

    #########################################
    # merging tri-alignments
    parser_merge = commands.add_parser('merge', help='Merge a series of Tri-alignments files')
    parser_merge.add_argument('--input', required=True, metavar='<PATH>[,<PATH>]', help='A comma-separated list of paths to Tri-alignments files (e.g. `*.tri-alignments.tsv.bgz`). Each PATH can be a pattern that contain `*` to match several files.')
    parser_merge.add_argument('--output_dir', default='./tri-alignments_merged/', metavar='<PATH>',
                              help='Output directory where the merged triplet will be stored (default: %(default)s)')
    parser_merge.add_argument('--output_name', default=None, metavar='<FILENAME>',
                              help='Output file name for the merged Tri-alignments. If not provided, the output is stored using the first input Tri-alignments filename, with a `.merged.tri-alignments.tsv.bgz` extension')
    parser_merge.add_argument('--memory', default='2G', help='Amount of memory (in Gigabyte unit) that can be used by `merge` program (default: "%(default)s")')
    parser_merge.add_argument('--threads', default=4, type=int, metavar='<INTEGER>', help='Number of threads that can be used by `sort` program (default: "%(default)s")')
    parser_merge.add_argument('--concatenate', action="store_true", help='Perform a simple concatenation of Tri-alignments files instead of merging files in a sorted manner')
    parser_merge.add_argument('--check_coverage', action="store_true", help='Checks whether merging chunks are overlapping, or if a chromosomal region is not covered by any chunk')
    parser_merge.add_argument('--sort_by', choices=['none', 'chrom'], default='chrom',
                              help='Sort the input files before merge/concatenation. `none` ignores sorting. `chrom` sorts files by the order of chromosomes in the original BAM file (default: "%(default)s")')
    # todo: add possibility to update the header/meta-data of the merged dataset, e.g. experiment_name
    # todo: implement a better header merger. Then remove this flag
    parser_merge.add_argument('--ignore_samheaders', action="store_true", help='Ignores merging sam headers.')
    parser_merge.add_argument('--metadata', default=None, metavar='<STRING>:<STRING>,[...]', help='A comma-separated list of key:values to be stored in the Tri-alignments file header such as experiment or assay name')
    parser_merge.set_defaults(func=cli_merge)

    #########################################
    # indexing tri-alignments
    parser_index = commands.add_parser('index', help='Index a tri-alignment file')
    parser_index.add_argument('--input', required=True, metavar='<PATH>', help='Path to a Tri-alignments file (e.g. `*.tri-alignments.tsv.bgz`). The index will be stored besides the input Tri-alignments file')
    parser_index.set_defaults(func=cli_index)

    #########################################
    # mapping tri-alignments into bins
    parser_bin = commands.add_parser('bin', help='Discretize the genome into equally-spaced anchors (i.e., bins) and represent the interactions in terms of Triplets')
    parser_bin.add_argument('--input', required=True, metavar='<PATH>', help='Path to input Tri-alignments file (e.g. `*.tri-alignments.tsv.bgz`).')
    parser_bin.add_argument('--output_dir', default='./triplets/', metavar='<PATH>',
                            help='Output directory where the Triplets file will be stored (default: %(default)s)')
    parser_bin.add_argument('--output_name', default=None, metavar='<FILENAME>',
                            help='Output name for the Triplets file. If not provided, the output is stored using the input Tri-alignments file name, with a `.triplets.h5` extension')
    parser_bin.add_argument('--chunk_chrom', required=True, metavar='<STRING>', help='Name of the chromosome from which triplet are formed')
    parser_bin.add_argument('--chunk_start', required=True, type=float, metavar='<INTEGER>', help='Start position of the chunk from which triplets are formed')
    parser_bin.add_argument('--chunk_end', required=True, type=float, metavar='<INTEGER>', help='End position of the chunk from which triplets are formed')
    parser_bin.add_argument('--anchor_width', default=int(25e3), type=float, metavar='<INTEGER>', help='Width of each anchor (i.e., genomic bin) (default: "%(default)s")')
    parser_bin.add_argument('--anchor_max_distance', default=int(2e6), type=float, metavar='<INTEGER>', help='Maximum distance between anchors of a triplet (default: "%(default)s")')
    parser_bin.add_argument('--mapping_quality', default=5, type=int, metavar='<INTEGER>', help='Minimum mapping quality threshold to consider an alignment to be valid (default: "%(default)s")')
    parser_bin.set_defaults(func=cli_bin)

    #########################################
    # transform triplet counts
    parser_transform = commands.add_parser('transform', help='Transform the raw counts using the requested transformation.')
    parser_transform.add_argument('--input', required=True, metavar='<PATH>', help='Path to Triplets file (e.g. `*.triplets.h5`). This file needs to be indexed.')
    parser_transform.add_argument('--transform_name', choices=['Gaussian'], default='Gaussian', help='Transformation name')
    parser_transform.add_argument('--transform_params', default='{"kernel_width":15,"kernel_scale":1.0}', help='JSON-formatted parameters of the transformation (default: "%(default)s")')
    parser_transform.add_argument('--transform_label', default='observed', metavar='<STRING>', help='Each transformed column will be labeled using this parameter (default: "%(default)s")')
    parser_transform.add_argument('--chunk_chrom', required=True, metavar='<STRING>', help='Name of the chromosome from which triplets are collected')
    parser_transform.add_argument('--chunk_start', required=True, type=float, metavar='<INTEGER>', help='Start position of the chunk from which triplets are collected')
    parser_transform.add_argument('--chunk_end', required=True, type=float, metavar='<INTEGER>', help='End position of the chunk from which triplets are collected')
    parser_transform.add_argument('--min_distance', default=int(25e3), type=float, metavar='<INTEGER>', help='Minimum distance between anchors of a triplet (default: "%(default)s")')
    parser_transform.add_argument('--max_distance', default=int(2e6), type=float, metavar='<INTEGER>', help='Maximum distance between anchors of a triplet (default: "%(default)s")')
    parser_transform.set_defaults(func=cli_transform)

    #########################################
    # finding neighbors
    parser_findnei = commands.add_parser('kdtree', help='Construct a KDTree structure to efficiently find Triplet neighbors.')
    parser_findnei.add_argument('--input', required=True, metavar='<PATH>', help='Path to Triplets file (e.g. `*.triplets.h5`).')
    parser_findnei.add_argument('--output_dir', default='./kdtrees/', metavar='<PATH>',
                                help='Output directory where the KDTree will be stored (default: %(default)s)')
    parser_findnei.add_argument('--output_name', default=None, metavar='<FILENAME>',
                                help='Output file name for the KDTree. If not provided, the output is stored using the input Triplets filename, with a `.kdtree.joblib` extension.')
    parser_findnei.add_argument('--chroms', metavar='STRING[,STRING]', default=None, help='A comma-separated list of chromosome names to be used in KDTree construction. If not provided, all chromosomes will be used.')
    parser_findnei.add_argument('--factors', required=True, metavar='<PATH>|<COL>:<FUNC>[,<COL>:<FUNC>]', help='Path to correction factor definitions, or a comma-separated list of <column_name>:<normalization>')
    parser_findnei.add_argument('--target', required=True, default='observed_ABC', metavar='<STRING>', help='Name of the column to be used as "target", in the background model  (default: "%(default)s")')
    parser_findnei.add_argument('--n_samples', default=np.inf, type=float, help='Sets the maximum number of samples to be included in the KDTree (default: "%(default)s")')
    parser_findnei.set_defaults(func=cli_kdtree)

    #########################################
    # estimate enrichments
    parser_enrich = commands.add_parser('enrichment', help='Estimate the enrichments of (a chunk of) triplet.')
    parser_enrich.add_argument('--input', required=True, metavar='<PATH>', help='Path to Triplets file (e.g. `*.triplets.h5`).')
    parser_enrich.add_argument('--kdtree', required=True, metavar='<PATH>', help='Path to KDTree, constructed from the input Triplets file.')
    parser_enrich.add_argument('--chunk_chrom', required=True, metavar='<STRING>', help='Name of the chromosome from which the triplets are going to be collected')
    parser_enrich.add_argument('--chunk_start', required=True, type=float, metavar='<INTEGER>', help='Start position of the chunk from which the triplets are going to be collected')
    parser_enrich.add_argument('--chunk_end', required=True, type=float, metavar='<INTEGER>', help='End position of the chunk from which the triplets are going to be collected')
    parser_enrich.add_argument('--view_point', default=None, type=float, metavar='<INTEGER>', help='If given, only triplets that overlap with the viewpoint are considered')
    parser_enrich.add_argument('--n_neighbors', default=int(10e3), type=int, metavar='<INTEGER>', help='Number of neighbors to use during enrichment estimation (default: "%(default)s")')
    parser_enrich.set_defaults(func=cli_enrichment)

    #########################################
    # plotting
    parser_plot = commands.add_parser('plot', help='Plotting varied characteristic of a given input file.')
    command_plot = parser_plot.add_subparsers(
        title='available plots are',
        dest='type',
    )

    # plotting virtual-hic
    parser_virthic = command_plot.add_parser('virtual_hic', help='Generate a virtual HiC plot, depicting the requested columns (using `--columns`).')
    parser_virthic.add_argument('--input', required=True, metavar='<PATH>',
                                help='Path to input file. Multiple paths could be provided using comma-separated format. '
                                     + 'Wild chars (i.e., "*") are also supported. The input file could be a BAM, tri-alignment, or triplets file. '
                                     + 'In case of BAM or tri-alignment, the file  needs to be indexed.')
    parser_virthic.add_argument('--output_dir', default='./plots/', metavar='<PATH>',
                                help='Output directory where the plot will be stored (default: %(default)s)')
    parser_virthic.add_argument('--output_name', default=None, metavar='<FILENAME>',
                                help='Output file name for the plot. If not provided, the output is stored using the input filename, with a `.pdf` extension.')
    parser_virthic.add_argument('--view_chrom', required=True, metavar='<STRING>', help='Name of the chromosome from which contact data are collected')
    parser_virthic.add_argument('--view_start', required=True, type=float, metavar='<INTEGER>', help='Start position of the chunk from which counts are collected')
    parser_virthic.add_argument('--view_end', required=True, type=float, metavar='<INTEGER>', help='End position of the chunk from which contact data are collected')
    parser_virthic.add_argument('--view_point', required=True, type=float, metavar='<INTEGER>', help='View point position that all contact data will interact to')
    parser_virthic.add_argument('--anchor_width', default=None, type=float, metavar='<INTEGER>', help='Width of each anchor (i.e., genomic bin). Only when then input file is a tri-alignment (default: "%(default)s")')
    parser_virthic.add_argument('--columns', default='count_AB,count_AC,count_ABC', metavar='<STRING>', help='A comma-separated list of column names that should be plotted (default: "%(default)s")')
    parser_virthic.add_argument('--plot_params', default=None, metavar='<STRING>', help='JSON-formatted parameters of each plot (default: "%(default)s")')
    parser_virthic.add_argument('--mapping_quality', default=5, type=int, metavar='<INTEGER>', help='Minimum mapping quality threshold to consider an alignment to be valid (default: "%(default)s")')
    parser_virthic.set_defaults(func=cli_plot_virtual_hic)

    # plotting hic
    parser_hic = command_plot.add_parser('hic', help='Generate a pairwise HiC plot, depicting the requested columns (using `--columns`).')
    parser_hic.add_argument('--input', required=True, metavar='<PATH>', help='Path to input BAM files. Multiple paths could be provided using comma-separated format. Wild chars (i.e., "*") are also supported.')
    parser_hic.add_argument('--output_dir', default='./plots/', metavar='<PATH>',
                            help='Output directory where the plot will be stored (default: %(default)s)')
    parser_hic.add_argument('--output_name', default=None, metavar='<FILENAME>',
                            help='Output file name for the plot. If not provided, the output is stored using the input filename, with a `.pdf` extension.')
    parser_hic.add_argument('--view_chrom', required=True, metavar='<STRING>', help='Name of the chromosome from which contact data are collected')
    parser_hic.add_argument('--view_start', required=True, type=float, metavar='<INTEGER>', help='Start position of the chunk from which counts are collected')
    parser_hic.add_argument('--view_end', required=True, type=float, metavar='<INTEGER>', help='End position of the chunk from which contact data are collected')
    parser_hic.add_argument('--anchor_width', default=None, type=float, metavar='<INTEGER>', help='Width of each anchor (i.e., genomic bin). Only when then input file is a tri-alignment (default: "%(default)s")')
    parser_hic.add_argument('--columns', default='count_AB,count_AC,count_ABC', metavar='<STRING>', help='A comma-separated list of column names that should be plotted (default: "%(default)s")')
    parser_hic.add_argument('--params', default=None, metavar='COLUMN-NAME:PARAM-NAME=PARAM-VALUE[,...]', help='A comma-separated list of column names and their corresponding parameteres and values')
    parser_hic.add_argument('--mapping_quality', default=5, type=int, metavar='<INTEGER>', help='Minimum mapping quality threshold to consider an alignment to be valid (default: "%(default)s")')
    parser_hic.set_defaults(func=cli_plot_hic)

    # plotting processing history
    parser_proc_hist = command_plot.add_parser('processing_history', help='Plot the processing history of the given input file.')
    parser_proc_hist.add_argument('--input', required=True, metavar='<PATH>', help='Path to Concatemers, Tri-alignments or Triplets file.')
    parser_proc_hist.add_argument('--output_dir', default='./plots/', metavar='<PATH>',
                                  help='Output directory where the plot will be stored (default: %(default)s)')
    parser_proc_hist.add_argument('--output_name', default=None, metavar='<FILENAME>',
                                  help='Output file name for the plot. If not provided, the output is stored using the input filename, with `.processing-history.pdf` suffix.')
    parser_proc_hist.add_argument('--igraph_params', default=None, metavar='<STRING>:<STRING>[,<STRING>:<STRING>]', help='A comma-separated list of key:value parameters. Will be sent directly to igraph for plotting.')
    parser_proc_hist.set_defaults(func=cli_plot_processing_history)

    # plotting read length histogram
    parser_hist_read_len = command_plot.add_parser('read_length', help='Plot the read length histogram of concatemers stored in the input file.')
    parser_hist_read_len.add_argument('--input', required=True, metavar='<PATH>', help='Path to Concatemers file.')
    parser_hist_read_len.add_argument('--output_dir', default='./plots/', metavar='<PATH>',
                                      help='Output directory where the plot will be stored (default: %(default)s)')
    parser_hist_read_len.add_argument('--output_name', default=None, metavar='<FILENAME>',
                                      help='Output file name for the plot. If not provided, the output is stored using the input filename, following `read-length.<filename>.pdf` pattern.')
    parser_hist_read_len.set_defaults(func=cli_plot_read_length_histogram)

    # plotting alignment length histogram
    parser_hist_aln_len = command_plot.add_parser('alignment_length', help='Plot the alignment length histogram of concatemers stored in the input file.')
    parser_hist_aln_len.add_argument('--input', required=True, metavar='<PATH>', help='Path to Concatemers file.')
    parser_hist_aln_len.add_argument('--output_dir', default='./plots/', metavar='<PATH>',
                                     help='Output directory where the plot will be stored (default: %(default)s)')
    parser_hist_aln_len.add_argument('--output_name', default=None, metavar='<FILENAME>',
                                     help='Output file name for the plot. If not provided, the output is stored using the input filename, following `alignment-length.<filename>.pdf` pattern.')
    parser_hist_aln_len.add_argument('--mapping_quality', default=5, type=int, metavar='<INTEGER>', help='Minimum mapping quality threshold to consider an alignment to be valid (default: "%(default)s")')
    parser_hist_aln_len.add_argument('--max_length', default=int(3e3), type=float, metavar='<INTEGER>', help='Minimum mapping quality threshold to consider an alignment to be valid (default: "%(default)s")')
    parser_hist_aln_len.set_defaults(func=cli_plot_alignment_length_histogram)

    #########################################
    # calculating statistics
    parser_stats = commands.add_parser('stat', help='Generate statistics from a given input file.')
    command_stat = parser_stats.add_subparsers(
        title='available analyses are',
        dest='analysis',
    )

    parser_decay = command_stat.add_parser('decay', help='Calculates decay stats for a given Concatemers file.')
    parser_decay.add_argument('--input', required=True, metavar='<PATH>', help='Path to input Concatemers file (e.g. `*.concatemers.h5`).')
    parser_decay.add_argument('--output_dir', default='./stats/', metavar='<PATH>',
                              help='Output directory where the stats will be stored (default: %(default)s)')
    parser_decay.add_argument('--output_name', default=None, metavar='<FILENAME>',
                              help='Output file name. If not provided, the output is stored using the input Concatemers filename, with a `.tsv` extension.')
    parser_decay.set_defaults(func=cli_stat_decay)


    return parser_main
