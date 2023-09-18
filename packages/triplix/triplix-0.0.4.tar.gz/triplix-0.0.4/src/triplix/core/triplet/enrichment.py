
import os
import time
import pathlib
import json

import numpy as np
import joblib

from triplix.core import configurations
from triplix.core.triplets import TripletsContainer
from triplix.core.utilities import generate_prog_id, overlap
from triplix._logging import get_logger

COMMAND_NAME = 'triplix.enrichment'
COMMAND_ID = f'{COMMAND_NAME}>{generate_prog_id()}'
logger = get_logger(COMMAND_NAME)


class EnrichmentEstimator:

    def __init__(self, triplet_path, kdtree_path):
        self.triplet_path = pathlib.Path(triplet_path).expanduser()
        self.kdtree_path = pathlib.Path(kdtree_path).expanduser()
        assert self.triplet_path.is_file(), f'Triplet file is not found: {self.triplet_path}'
        assert self.kdtree_path.is_file(), f'KDTree file is not found: {self.kdtree_path}'
        logger.info(f'Using KDTree: {kdtree_path}')

    def estimate_enrichments(self, chunk_chrom, chunk_start, chunk_end, n_neighbors, view_point=None):

        # load KDTree
        logger.info(f'Loading KDTree: size={os.stat(self.kdtree_path).st_size / 1e9:0.1f}GB')
        data = joblib.load(self.kdtree_path)
        kdtree = data['kdtree']
        metadata = data['metadata']
        del data
        feature2index = metadata['feature2index']
        factors_id = metadata["factors_id"]
        n_feature = len(feature2index)
        logger.info(
            f'KDTree is loaded. Details: '
            f'factors_id="{factors_id}"; '
            f'#sample={metadata["n_sample"]:,d}; '
            f'#feature={n_feature:,d}'
        )
        assert n_feature == metadata["n_feature"]

        # load triplets
        chunk_start = int(chunk_start)
        chunk_end = int(chunk_end)
        with TripletsContainer(container_path=self.triplet_path, exclusive=True) as triplets_obj:
            chrom_lengths = dict(zip(
                triplets_obj.properties['chrom_names'],
                triplets_obj.properties['chrom_lengths']
            ))
            chrom_size = chrom_lengths[chunk_chrom]
            if chunk_start > chrom_size:
                logger.info(f'The requested window ({chunk_start / 1e6:0.2f}-{chunk_end / 1e6:0.2f}mb) '
                            f'is outside of {chunk_chrom} (length={chrom_size / 1e6:0.2f}mb). '
                            f'No processing is needed.')
                return
            logger.info(f'Area of interest is: {chunk_chrom}:{chunk_start:0,d}-{chunk_end:0,d}. ')

            # load triplets from the container
            logger.info(f'Loading triplets from: {self.triplet_path}')
            triplets = triplets_obj.fetch(
                chrom_a=chunk_chrom, start_a=chunk_start, end_a=chunk_end - 1,
                columns=['start_A', 'start_B', 'start_C'] + list(feature2index.keys()) + [metadata['target_name']],
                exclusive=False,
            )
            logger.debug(f'First fetched triplet: {triplets[0]["start_A"][0]:,d}-{triplets[0]["start_B"][0]:,d}-{triplets[0]["start_C"][0]:,d}')
            logger.debug(f'Last fetched triplet: {triplets[-1]["start_A"][0]:,d}-{triplets[-1]["start_B"][0]:,d}-{triplets[-1]["start_C"][0]:,d}')
            n_sample = len(triplets)
            logger.info(f'{n_sample:,d} triplets are loaded.')

            # sub-selecting triplets, if requested
            if view_point is not None:
                view_point = int(view_point)
                vp_end = view_point + triplets_obj.properties['anchor_width']
                logger.info(f'Sub-selecting triplets to overlap with: {view_point:,d}-{vp_end:,d}')
                # vp_start, view_start, view_end = int(21.775e6), int(21.00e6), int(23.500e6)
                # vp_start, view_start, view_end = int(119.825e6), int(119.300e6), int(121.300e6)

                # filter the collected triplets to overlap with the requested interval
                trp_tmp = triplets.sort_anchors(by=view_point, force_upper=True)
                within_interval = (
                        (overlap(query_start=view_point,   query_end=vp_end - 1,   ref_start=trp_tmp['start_A'], ref_end=trp_tmp['start_A'] + triplets_obj.properties['anchor_width'] - 1)) &
                        (overlap(query_start=chunk_start, query_end=chunk_end - 1, ref_start=trp_tmp['start_B'], ref_end=trp_tmp['start_B'] + triplets_obj.properties['anchor_width'] - 1)) &
                        (overlap(query_start=chunk_start, query_end=chunk_end - 1, ref_start=trp_tmp['start_C'], ref_end=trp_tmp['start_C'] + triplets_obj.properties['anchor_width'] - 1))
                )
                del trp_tmp
                triplets = triplets[within_interval]
                n_sample = len(triplets)
                logger.info(f'{n_sample:,d} triplets are left after filtering.')

        # prepare the dataset
        dataset = np.zeros([n_sample, n_feature], dtype=float)
        for col_name, feat_idx in feature2index.items():
            dataset[:, feat_idx] = triplets[col_name]
        observed = np.array(triplets[metadata['target_name']], dtype=float)

        # normalize the loaded features
        logger.info(f'Normalizing the loaded features ...')
        for norm_idx, norm in enumerate(metadata["factors"]):
            logger.debug(f'\tStep {norm_idx + 1}, performing: {norm}')
            assert norm['class'] == 'normalization'
            col_name = norm['column']
            feat_idx = feature2index[col_name]
            if norm['type'] == 'zscore':
                dataset[:, feat_idx] = (dataset[:, feat_idx] - norm['mean']) / norm['std']
            else:
                raise ValueError(f'Unknown normalization type: {norm["type"]}')

        # add estimation columns
        estimation_columns = [
            f'{factors_id}.neighbors_distance.med',
            f'{factors_id}.neighbors_distance.std',
            f'{factors_id}.neighbors_expected.avg',
            f'{factors_id}.neighbors_expected.std',
            f'{factors_id}.enrichment',
        ]
        for col_name in estimation_columns:
            triplets[col_name] = np.full(n_sample, fill_value=np.nan)

        # estimating the enrichments
        logger.info('Estimating enrichments ...')
        n_processed = 0
        n_ignore = 0
        logger.log_time = time.time()
        for trp_idx in range(n_sample):
            if time.time() - logger.log_time > configurations.configs['log_interval']:
                logger.log_time = time.time()
                logger.info(
                    f'{trp_idx + 1:10,d}/{n_sample:,d} currently at {chunk_chrom}:'
                    f'{triplets["start_A"][trp_idx]:,d}-'
                    f'{triplets["start_B"][trp_idx]:,d}-'
                    f'{triplets["start_C"][trp_idx]:,d} | '
                    f'triplets stats: #ignored:{n_ignore:,d}'
                )

            # find neighbors, per triplet
            nei_distances, nei_indices = kdtree.query(dataset[[trp_idx]], k=n_neighbors)
            # assert nei_distances.shape == nei_indices.shape == (1, n_neighbors)
            nei_distances = nei_distances[0]
            nei_indices = nei_indices[0]
            # np.vstack([dataset[[trp_idx]], kdtree.get_arrays()[0][nei_indices]])

            # find neighbors' target values
            bkg_obs = metadata['target_values'][nei_indices].copy()

            # clip the top/bottom 1% of the distribution
            bkg_lim = np.percentile(bkg_obs, [1, 99])
            is_valid = (bkg_lim[0] < bkg_obs) & (bkg_obs < bkg_lim[1])
            bkg_obs = bkg_obs[is_valid]
            nei_distances = nei_distances[is_valid]
            # nei_indices = nei_indices[is_val]
            if len(bkg_obs) == 0:
                n_ignore += 1
                continue

            # record neighbor details
            triplets[f'{factors_id}.neighbors_distance.med'][trp_idx] = np.median(nei_distances).round(decimals=3)
            triplets[f'{factors_id}.neighbors_distance.std'][trp_idx] = np.std(nei_distances).round(decimals=3)

            # compute enrichments
            neigh_exp_avg = np.mean(bkg_obs)
            neigh_exp_std = np.std(bkg_obs)
            triplets[f'{factors_id}.neighbors_expected.avg'][trp_idx] = neigh_exp_avg.round(decimals=3)
            triplets[f'{factors_id}.neighbors_expected.std'][trp_idx] = neigh_exp_std.round(decimals=3)

            if neigh_exp_std > 0:
                enrichment = (observed[trp_idx] - neigh_exp_avg) / neigh_exp_std
            else:
                enrichment = np.nan
            triplets[f'{factors_id}.enrichment'][trp_idx] = np.round(enrichment, decimals=3)
            n_processed += 1
        logger.info(f'Cached {n_processed:,d} enrichments')

        # delete redundant columns
        for col_name in list(triplets.keys()):
            if col_name not in ['start_A', 'start_B', 'start_C'] + estimation_columns:
                logger.debug(f'Redundant column is deleted from memory: "{col_name}"')
                del triplets[col_name]

        # storing the enrichments
        logger.info(f'Storing {n_processed:,d} triplet enrichments to: {self.triplet_path}')
        with TripletsContainer(container_path=self.triplet_path, exclusive=True) as triplets_obj:

            # storing triplets
            triplets_obj.store(
                triplets=triplets,
                chrom_a=chunk_chrom,
                exclusive=False,
                verify_coords=True,
            )

            # add processed chunk
            triplets_obj.add_stored_chunk(
                [chunk_chrom, chunk_start, chunk_end],
                exclusive=False
            )

            # add transformations
            logger.debug(f'Storing transformations:')
            cis_path = triplets_obj.experiment_path + f'/contacts/triplets/{chunk_chrom},{chunk_chrom},{chunk_chrom}/'
            for ds_name in [f'{factors_id}.enrichment']:
                transformations = list()
                # for norm_info in metadata["normalizations"]:
                #     if norm_info['column'] == ds_name:
                #         transformations.append(norm_info.copy())
                transformations.append({
                    'id': f'{ds_name}:enrichment:zscore',
                    'factors_id': factors_id,
                    'class': 'enrichment',
                    'type': 'zscore',
                    'kdtree_path': str(self.kdtree_path),
                })

                triplets_obj.store_attribute(
                    dataset_path=f'{cis_path}/{ds_name}',
                    name='transformations', value=json.dumps(transformations),
                    exclusive=False,
                )
                logger.debug(f'\t"{ds_name}": {transformations}')

        logger.info(f'Enrichment estimation is finished successfully: '
                    f'#triplet:{n_processed:,d}; '
                    f'#ignored:{n_ignore:,d}; '
                    f'file size:{os.stat(self.triplet_path).st_size / 1e9:0,.1f}GB')
