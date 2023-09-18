import time
import pathlib

import numpy as np

from triplix.core.triplets import TripletsContainer, Triplets
from triplix.core.header import TriplixHeader
from triplix.core import configurations
from triplix.core.tri_alignments import TriAlignmentsContainer
from triplix.core.utilities import generate_prog_id
from triplix._logging import get_logger

COMMAND_NAME = 'triplix.bin'
COMMAND_ID = f'{COMMAND_NAME}>{generate_prog_id()}'
logger = get_logger(COMMAND_NAME)


class TriAlignmentBinner:
    datasets_info = {
        'dist_AB': {'dtype': 'uint32'},
        'dist_AC': {'dtype': 'uint32'},
        'dist_BC': {'dtype': 'uint32'},
        'count_A': {'dtype': 'uint32'},
        'count_B': {'dtype': 'uint32'},
        'count_C': {'dtype': 'uint32'},
        'count_AB': {'dtype': 'uint32'},
        'count_AC': {'dtype': 'uint32'},
        'count_BC': {'dtype': 'uint32'},
        'count_ABC': {'dtype': 'uint32'},
    }

    def __init__(self, input_path, anchor_width, anchor_max_distance, output_dir=None, output_name=None):
        self.input_path = pathlib.Path(input_path).expanduser()
        self.header = TriplixHeader(file_path=input_path)
        self.output_dir = output_dir
        self.output_name = output_name

        if output_dir is None:
            output_dir = self.input_path.parent
        if output_name is None:
            output_name = self.header.experiment_name + '.triplets.h5'
        self.output_path = pathlib.Path(output_dir).expanduser() / output_name
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

        # open or initialize the container
        self.trpl_container = TripletsContainer(
            container_path=self.output_path,
            tri_alignments_path=self.input_path,
            anchor_width=anchor_width,
            anchor_max_distance=anchor_max_distance,
            auto_init=True,
        )

    def bin(self, chunk_chrom, chunk_start, chunk_end, mapping_quality):

        # define chunk area
        chunk_start = int(chunk_start)
        chunk_end = int(chunk_end)
        chrom_size = self.header.chrom_lengths[chunk_chrom]
        if chunk_start > chrom_size:
            logger.info(f'The requested window ({chunk_start / 1e6:0.2f}-{chunk_end / 1e6:0.2f}mb) '
                        f'is outside of {chunk_chrom} (length={chrom_size / 1e6:0.2f}mb). '
                        f'No processing is needed.')
            return
        logger.info(f'Area of interest is: '
                    f'{chunk_chrom}:{chunk_start:0,d}-{chunk_end:0,d}. ')

        # define anchors
        anchor_width = self.trpl_container.properties['anchor_width']
        anchor_max_distance = self.trpl_container.properties['anchor_max_distance']
        chunk_edge = anchor_max_distance
        load_beg = max(0, chunk_start - chunk_edge)
        load_end = min(chrom_size, chunk_end + chunk_edge)
        anchor_edges = np.arange(load_beg, load_end + anchor_width, anchor_width, dtype=int)
        n_anchor = len(anchor_edges) - 1
        logger.info(f'{n_anchor} anchors (width={anchor_width / 1e3:0.0f}kb) are formed over '
                    f'{chunk_chrom}:{anchor_edges[0]:0,d}-{anchor_edges[-1]:0,d}. '
                    f'This area includes {chunk_edge / 1e6:0.2f}mb "edge" bins.')

        # prepare Triplet selector
        logger.info(f'Loading tri-alignments from: {self.input_path}')
        tri_container = TriAlignmentsContainer(trialn_path=self.input_path)

        # loop over Tri-alignments and populate the Triplets count matrix
        logger.info('Mapping tri-alignments to triplets ...')
        counts = np.zeros([n_anchor, n_anchor, n_anchor], dtype=int)
        n_load = 0
        logger.log_time = 0
        for ai in range(n_anchor):
            if time.time() - logger.log_time > configurations.configs['log_interval']:
                logger.log_time = time.time()
                logger.info(f'\tcurrently at {anchor_edges[ai]:,d} ({ai:3d}/{n_anchor}) anchor, and loaded {n_load:,d} (unique) tri-alignments')
            if anchor_edges[ai] >= chunk_end:
                logger.debug(f'End of chunk is reached, ignoring the rest.')
                break
            if anchor_edges[ai] > chrom_size:
                logger.debug(f'End of chromosome {chunk_chrom} ({chrom_size:,d}bp) is reached, ignoring the rest.')
                break
            counts[ai, :, :] = tri_container.fetch_slice(
                vp_chrom=chunk_chrom, vp_start=anchor_edges[ai], vp_end=anchor_edges[ai + 1] - 1,
                anchor_edges=anchor_edges,
                anchor_max_distance=anchor_max_distance,
                mapping_quality=mapping_quality
            )
            n_load += np.sum(counts[ai, :, :])

        if n_load == 0:
            logger.warning('No tri-alignment was found in this interval.')
        else:
            logger.info(f'In total, loaded {n_load:0,d} tri-alignments, and used {counts.sum():,d} filtered tri-alignments.')

        # defining triplets
        triplet_columns = [
            'start_A', 'start_B', 'start_C',
            'distance_AB', 'distance_AC', 'distance_BC',
            'count_A', 'count_B', 'count_C',
            'count_AB', 'count_AC', 'count_BC',
            'count_ABC'
        ]
        triplets = Triplets(columns=triplet_columns)

        # storing triplet counts
        logger.info(f'Storing triplets to: {self.output_path}')
        logger.log_time = 0
        n_cache = 0
        n_store = 0
        batch_size = configurations.configs['triplets']['batch_size']
        for ai in range(n_anchor):
            if anchor_edges[ai] < chunk_start:
                continue
            if anchor_edges[ai] >= chunk_end:
                logger.debug(f'End of chunk is reached, ignoring the rest.')
                break
            if anchor_edges[ai] > chrom_size:  # overlap with the end of chromosome generates the last triplet.
                logger.debug(f'End of chromosome {chunk_chrom} ({chrom_size:,d} bp) is reached, ignoring the rest.')
                break
            for aj in range(ai, n_anchor):
                for ak in range(aj, n_anchor):
                    if anchor_edges[ak] - anchor_edges[ai] > anchor_max_distance:
                        break
                    if time.time() - logger.log_time > configurations.configs['log_interval']:
                        logger.log_time = time.time()
                        logger.info(f'\tcurrently at {anchor_edges[ai]:,d} ({ai:3d}/{n_anchor}) anchor, and cached {n_cache:,d} triplets')

                    triplets['start_A'].append(anchor_edges[ai])
                    triplets['start_B'].append(anchor_edges[aj])
                    triplets['start_C'].append(anchor_edges[ak])

                    triplets['distance_AB'].append(anchor_edges[aj] - anchor_edges[ai])
                    triplets['distance_AC'].append(anchor_edges[ak] - anchor_edges[ai])
                    triplets['distance_BC'].append(anchor_edges[ak] - anchor_edges[aj])

                    triplets['count_A'].append(counts[ai, :, :].sum() + counts[:, ai, :].sum() + counts[:, :, ai].sum())
                    triplets['count_B'].append(counts[aj, :, :].sum() + counts[:, aj, :].sum() + counts[:, :, aj].sum())
                    triplets['count_C'].append(counts[ak, :, :].sum() + counts[:, ak, :].sum() + counts[:, :, ak].sum())

                    triplets['count_AB'].append(counts[ai, aj, :].sum() + counts[ai, :, aj].sum() + counts[:, ai, aj].sum())
                    triplets['count_AC'].append(counts[ai, ak, :].sum() + counts[ai, :, ak].sum() + counts[:, ai, ak].sum())
                    triplets['count_BC'].append(counts[aj, ak, :].sum() + counts[aj, :, ak].sum() + counts[:, aj, ak].sum())

                    triplets['count_ABC'].append(counts[ai, aj, ak])
                    n_cache += 1

                    # store if enough are cached
                    if n_cache >= batch_size:
                        logger.info(f'\tstoring {n_cache:,d} cached triplets.')
                        self.trpl_container.store(triplets=triplets, chrom_a=chunk_chrom, verify_coords=False)
                        n_store += n_cache
                        triplets.clear()
                        n_cache = 0
        if n_cache > 0:
            logger.info(f'\tstoring {n_cache:,d} cached triplets.')
            self.trpl_container.store(triplets=triplets, chrom_a=chunk_chrom, verify_coords=False)

        # update stored chunks
        self.trpl_container.add_stored_chunk([chunk_chrom, chunk_start, chunk_end], exclusive=True)

        logger.info(f'In total, {n_store:,d} triplets are stored successfully.')

