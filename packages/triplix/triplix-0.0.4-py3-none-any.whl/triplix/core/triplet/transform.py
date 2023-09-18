import time
import pathlib
import json

import numpy as np
import scipy.signal as signal

from triplix.core import configurations
from triplix.core.triplets import TripletsContainer, Triplets
from triplix.core.utilities import generate_prog_id
from triplix._logging import get_logger

COMMAND_NAME = 'triplix.transform'
COMMAND_ID = f'{COMMAND_NAME}>{generate_prog_id()}'
logger = get_logger(COMMAND_NAME)


def gauss_kernel_3d(width, sigma):
    if sigma == 0:
        kernel = np.zeros([width, width, width])
        kernel[width // 2, width // 2, width // 2] = 1.0
    else:
        dx, dy, dz = np.mgrid[
                     -width // 2 + 1:width // 2 + 1,
                     -width // 2 + 1:width // 2 + 1,
                     -width // 2 + 1:width // 2 + 1]

        kernel = np.exp(-((dx ** 2 + dy ** 2 + dz ** 2) / (2.0 * sigma ** 2)))
    return kernel / float(kernel.sum())

    # import matplotlib.pyplot as plt
    # from mpl_toolkits.mplot3d import Axes3D
    # krn = (gauss_kernel_3d(10, 2) * 1000).astype(int)
    # z, x, y = krn.nonzero()
    # fig = plt.figure()
    # ax = Axes3D(fig)
    # plt.close('all')
    # fig = plt.figure()
    # ax = fig.gca(projection='3d')
    # ax.scatter(x, y, z, c=-krn[x, y, z], alpha=0.5)
    # plt.show()


class GaussianSmoother:

    def __init__(self, triplet_path):
        self.triplet_path = pathlib.Path(triplet_path).expanduser()

    def smooth(
            self,
            chunk_chrom, chunk_start, chunk_end,
            kernel_width, kernel_scale,
            min_distance, max_distance,
            label
    ):

        # collecting relevant triplets
        with TripletsContainer(container_path=self.triplet_path, exclusive=True) as triplets_obj:
            logger.debug(f'Container is locked, ready to collect triplets: {self.triplet_path}')

            # define the chunk area
            chunk_start = int(chunk_start)
            chunk_end = int(chunk_end)
            anchor_width = triplets_obj.properties['anchor_width']
            chrom_lengths = dict(zip(triplets_obj.properties['chrom_names'], triplets_obj.properties['chrom_lengths']))
            chrom_size = chrom_lengths[chunk_chrom]
            if chunk_start > chrom_size:
                logger.info(f'The requested window ({chunk_start / 1e6:0.2f}-{chunk_end / 1e6:0.2f}mb) '
                            f'is outside of {chunk_chrom} (length={chrom_size / 1e6:0.2f}mb). '
                            f'No processing is needed.')
                return
            logger.info(f'Area of interest is: {chunk_chrom}:{chunk_start:0,d}-{chunk_end:0,d}. ')

            # define anchor edges
            chunk_edge = max_distance
            load_beg = max(0, chunk_start - chunk_edge)
            load_end = min(chrom_size, chunk_end + chunk_edge)
            anchor_edges = np.arange(load_beg, load_end + anchor_width, anchor_width, dtype=int)
            n_anchor = len(anchor_edges) - 1
            logger.info(f'{n_anchor} anchors (width={anchor_width / 1e3:0.0f}kb) are formed over '
                        f'{chunk_chrom}:{anchor_edges[0]:0,d}-{anchor_edges[-1]:0,d}. '
                        f'This area includes {chunk_edge / 1e6:0.2f}mb "edge" anchors.')

            # prepare Triplet selector
            logger.info(f'Loading triplets from: {self.triplet_path}')
            triplets_input = triplets_obj.fetch(
                chrom_a=chunk_chrom, start_a=anchor_edges[0], end_a=anchor_edges[-1] - 1,
                chrom_b=chunk_chrom, start_b=anchor_edges[0], end_b=anchor_edges[-1] - 1,
                chrom_c=chunk_chrom, start_c=anchor_edges[0], end_c=anchor_edges[-1] - 1,
                columns=['start_A', 'start_B', 'start_C', 'count_ABC'],
                exclusive=False,
            )
        # pd.DataFrame(triplets_input)

        # map triplets to data cubes
        logger.info('Mapping triplets to a cube of counts ...')
        counts_upper = triplets_input.to_cube(anchor_edges=anchor_edges, value_column='count_ABC')
        counts_upper[np.isnan(counts_upper)] = 0
        counts_upper = counts_upper.astype(int)
        logger.info(f'In total, {counts_upper.sum():,d} triplet contacts are collected.')

        # store counts to a full symmetric cube, ignoring invalid values to prepare for smoothening
        logger.info(f'Making the cube of counts symmetric ...')
        symmetric = np.zeros([n_anchor, n_anchor, n_anchor], dtype=float)
        for ai in range(n_anchor):
            for aj in range(ai, n_anchor):
                for ak in range(aj, n_anchor):
                    if not min_distance <= anchor_edges[aj] - anchor_edges[ai] <= max_distance:
                        continue
                    if not min_distance <= anchor_edges[ak] - anchor_edges[ai] <= max_distance:
                        continue
                    if not min_distance <= anchor_edges[ak] - anchor_edges[aj] <= max_distance:
                        continue
                    symmetric[ai, aj, ak] = counts_upper[ai, aj, ak]
                    symmetric[ai, ak, aj] = counts_upper[ai, aj, ak]
                    symmetric[aj, ai, ak] = counts_upper[ai, aj, ak]
                    symmetric[aj, ak, ai] = counts_upper[ai, aj, ak]
                    symmetric[ak, ai, aj] = counts_upper[ai, aj, ak]
                    symmetric[ak, aj, ai] = counts_upper[ai, aj, ak]

        # smooth the counts
        logger.info(f'Smoothening the cube using a Gaussian kernel. Parameters: '
                    f'width={kernel_width:d}, '
                    f'scale={kernel_scale:0.2f}')
        kernel = gauss_kernel_3d(kernel_width, kernel_scale)
        # print((kernel[:, :, kernel_width // 2] * 1000).astype(int))
        smoothed = signal.convolve(symmetric, kernel, mode='same')
        # smoothed = np.round(smoothed, decimals=2)
        # temp = ndimage.convolve(cube.astype(float), kernel, mode='constant')
        # print(np.abs(smoothed - temp).sum())
        # smoothed = np.round(smoothed, 2)

        # collect valid values from smoothed cube
        logger.info(f'Collecting the upper-triangle of the smoothed counts ...')
        smoothed_triu = np.zeros([n_anchor, n_anchor, n_anchor], dtype=float)
        for ai in range(n_anchor):
            for aj in range(ai, n_anchor):
                for ak in range(aj, n_anchor):
                    # here we store everything, including smaller or larger distances:
                    # the farther or closer coverage is valid, as this coverage is from valid tripliets
                    # that are leaked/smoothed to invalid areas. So the leaked counts are also informative.
                    # if not min_distance <= anchor_edges[aj] - anchor_edges[ai] <= max_distance:
                    #     continue
                    # if not min_distance <= anchor_edges[ak] - anchor_edges[ai] <= max_distance:
                    #     continue
                    # if not min_distance <= anchor_edges[ak] - anchor_edges[aj] <= max_distance:
                    #     continue

                    smoothed_triu[ai, aj, ak] = smoothed[ai, aj, ak]
                    # in the counts below, we consider all directions, no need to store other axes
        # del smoothed

        # from matplotlib import pyplot as plt, cm
        # i = 20
        # plt.close('all')
        # cmap = cm.get_cmap('hot')
        # cmap.set_under('#0000ff')
        # clim = [0.1, np.nanpercentile(counts[i], q=100)]
        #
        # fig_h, axes = plt.subplots(1, 4, figsize=(15, 5), sharex='all', sharey='all')
        # axes = axes.ravel()
        # axes[0].imshow(counts[i, :120, :120], vmin=clim[0], vmax=clim[1], cmap=cmap)
        # axes[0].set_title(clim)
        # axes[1].imshow(symmetric[i, :120, :120], vmin=clim[0], vmax=clim[1], cmap=cmap)
        # axes[2].imshow(smoothed[i, :120, :120], vmin=clim[0], vmax=clim[1], cmap=cmap)
        # axes[3].imshow(upper_tri[i, :120, :120], vmin=clim[0], vmax=clim[1], cmap=cmap)

        # defining output triplets
        triplet_columns = [
            'start_A', 'start_B', 'start_C',
            f'{label}_A', f'{label}_B', f'{label}_C',
            f'{label}_AB', f'{label}_AC', f'{label}_BC',
            f'{label}_ABC', f'{label}_surround',
        ]
        triplets_output = Triplets(columns=triplet_columns)

        # storing Triplets counts
        logger.log_time = 0
        n_store = 0
        for ai in range(n_anchor):
            if not chunk_start <= anchor_edges[ai] < chunk_end:
                continue
            if anchor_edges[ai] > chrom_size:
                logger.debug(f'End of chromosome {chunk_chrom} ({chrom_size:,d} bp) is reached, ignoring the rest.')
                break
            for aj in range(ai, n_anchor):
                for ak in range(aj, n_anchor):
                    if not anchor_edges[aj] - anchor_edges[ai] <= max_distance:
                        continue
                    if not anchor_edges[ak] - anchor_edges[ai] <= max_distance:
                        continue
                    if not anchor_edges[ak] - anchor_edges[aj] <= max_distance:
                        continue
                    if time.time() - logger.log_time > configurations.configs['log_interval']:
                        logger.log_time = time.time()
                        logger.info(f'\tcurrently at {anchor_edges[ai]:,d} ({ai:3d}/{n_anchor}) anchor, and cached {n_store:,d} smoothed counts')

                    triplets_output['start_A'].append(anchor_edges[ai])
                    triplets_output['start_B'].append(anchor_edges[aj])
                    triplets_output['start_C'].append(anchor_edges[ak])

                    triplets_output[f'{label}_A'].append(smoothed_triu[ai, :, :].sum() + smoothed_triu[:, ai, :].sum() + smoothed_triu[:, :, ai].sum())
                    triplets_output[f'{label}_B'].append(smoothed_triu[aj, :, :].sum() + smoothed_triu[:, aj, :].sum() + smoothed_triu[:, :, aj].sum())
                    triplets_output[f'{label}_C'].append(smoothed_triu[ak, :, :].sum() + smoothed_triu[:, ak, :].sum() + smoothed_triu[:, :, ak].sum())

                    triplets_output[f'{label}_AB'].append(smoothed_triu[ai, aj, :].sum() + smoothed_triu[ai, :, aj].sum() + smoothed_triu[:, ai, aj].sum())
                    triplets_output[f'{label}_AC'].append(smoothed_triu[ai, ak, :].sum() + smoothed_triu[ai, :, ak].sum() + smoothed_triu[:, ai, ak].sum())
                    triplets_output[f'{label}_BC'].append(smoothed_triu[aj, ak, :].sum() + smoothed_triu[aj, :, ak].sum() + smoothed_triu[:, aj, ak].sum())

                    triplets_output[f'{label}_ABC'].append(smoothed_triu[ai, aj, ak])

                    triplets_output[f'{label}_surround'].append(
                        np.sum(smoothed_triu[
                               max(0, ai - 4):ai + 5,
                               max(0, aj - 4):aj + 5,
                               max(0, ak - 4):ak + 5])
                        - np.sum(smoothed_triu[
                                 max(0, ai - 2):ai + 3,
                                 max(0, aj - 2):aj + 3,
                                 max(0, ak - 2):ak + 3])
                    )

                    n_store += 1

        # rounding the counts
        for col_name in triplets_output.keys():
            if col_name.startswith(f'{label}_'):
                logger.debug(f'Rounding "{col_name}" counts to two decimals ...')
                triplets_output[col_name] = np.round(triplets_output[col_name], decimals=2)

        # storing the collected data/information
        with TripletsContainer(container_path=self.triplet_path, exclusive=True) as triplets_obj:

            # storing triplets
            triplets_obj.store(
                triplets=triplets_output,
                chrom_a=chunk_chrom,
                exclusive=False,
                verify_coords=True,
            )

            # add the new chunk to stored_chunks
            triplets_obj.add_stored_chunk([chunk_chrom, chunk_start, chunk_end], exclusive=False)

            # add transformation details
            logger.debug(f'Storing transformation details, per column:')
            cis_path = triplets_obj.experiment_path + f'/contacts/triplets/{chunk_chrom},{chunk_chrom},{chunk_chrom}/'
            for ds_name in triplets_output.keys():
                if ds_name.startswith(f'{label}_'):
                    transformation = {
                        'class': 'transformation',
                        'id': f'{ds_name}:Gaussian_smoothing:w{kernel_width},s{kernel_scale}',
                        'type': 'Gaussian_smoothing',
                        'width': kernel_width,
                        'scale': kernel_scale,
                        'source': 'count_ABC',
                    }
                    logger.debug(f'Added to "{ds_name}": {transformation}')
                    triplets_obj.store_attribute(
                        dataset_path=f'{cis_path}/{ds_name}',
                        name='transformations',
                        value=[json.dumps(transformation)],
                        exclusive=False,
                    )

            # updating attributes if needed
            # triplets_obj.retrieve_attributes(exclusive=False)
            # triplets_obj.store_attributes(exclusive=False)

        logger.info(f'{n_store:,d} triplets are updated with "{label}" transformation successfully.')
