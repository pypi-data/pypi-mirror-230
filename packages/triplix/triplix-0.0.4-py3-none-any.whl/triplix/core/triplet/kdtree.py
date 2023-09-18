
import os
import time
import pathlib
from importlib import resources
import hashlib
try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

import numpy as np
from sklearn.neighbors import KDTree
import joblib

from triplix.core import configurations
from triplix.core.triplets import TripletsContainer
from triplix.core.hdf5 import HDF5Container
from triplix._logging import get_logger

COMMAND_NAME = 'triplix.neighbor'
logger = get_logger(COMMAND_NAME)


class NeighborFinder:

    def __init__(self, triplet_path):
        self.triplet_path = pathlib.Path(triplet_path).expanduser()

    def find_neighbors(self, factors_info, target, chroms=None, output_dir=None, output_name=None, n_samples=np.inf):

        # load correction factor configs
        possible_paths = [
            pathlib.Path(factors_info).expanduser(),
            resources.files('triplix').joinpath(f'factor_configs/{factors_info}.toml')
        ]
        for file_path in possible_paths:
            if file_path.is_file():
                factors_id = file_path.stem
                with open(file_path, 'rb') as toml_file:
                    factors = tomllib.load(toml_file)['factors']
                break
        else:
            factors_id = 'unknown'
            factors = []
            for record in factors_info.split(','):
                col_name, norm_type = record.split(':')
                factors.append({'column': col_name, 'type': norm_type})
        assert len(factors) > 0, 'At least a single factor is required for KDTree construction.'

        # define output file name
        if output_dir is None:
            output_dir = self.triplet_path.parent
        if output_name is None:
            output_name = self.triplet_path.stem + f'.kdtree.{factors_id}.joblib'
        output_path = pathlib.Path(output_dir).expanduser() / output_name
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # map column names to feature indices
        feature2index = {}
        for factor in factors:
            if factor['column'] not in feature2index:
                feature2index[factor['column']] = len(feature2index)
        n_feature = len(feature2index)

        # collecting Triplets across the genome
        logger.info(f'Loading triplets from: {self.triplet_path}')
        dataset = [list() for _ in range(n_feature)]
        targets = []
        with TripletsContainer(container_path=self.triplet_path, exclusive=True) as triplets_obj:
            with HDF5Container(self.triplet_path, mode='r', exclusive=False) as container:

                # define chromosomes of interest
                triplets_ds = container.h5_file[triplets_obj.experiment_path]['contacts/triplets']
                if chroms is None:
                    cis_paths = list(triplets_ds.keys())
                else:
                    cis_paths = []
                    for chrom in chroms:
                        # if chrom == 'unmapped':
                        #     continue
                        cis_paths.append(f'{chrom},{chrom},{chrom}')

                # iterate over cis-triplets and collect relevant datasets
                for cis_path in cis_paths:
                    logger.info(f'collecting cis-triplets from: {cis_path} ...')
                    cis_ds = triplets_ds[cis_path]
                    for ds_name, feat_idx in feature2index.items():
                        logger.debug(f'\tfeature idx{feat_idx}: loading "{ds_name}", {cis_ds[ds_name].shape[0]:,d} elements ...')
                        dataset[feat_idx].extend(cis_ds[ds_name][()])

                    logger.debug(f'\ttarget: loading "{target}", {cis_ds[target].shape[0]:,d} elements ...')
                    targets.extend(cis_ds[target][()])
                    if len(targets) >= n_samples:
                        logger.info(f'Reached the maximum number of samples of {n_samples:0,.0f}. No more Triplets will be loaded.')
                        break

        # converting to numpy array
        logger.debug('Converting the dataset to Numpy 2D array')
        dataset = np.array(dataset, dtype=float).T
        targets = np.array(targets, dtype=float)
        logger.info(f'Triplet dataset has {dataset.shape[0]:,d} samples and {dataset.shape[1]:d} features.')

        # limit the number of samples, if requested
        if np.isfinite(n_samples):
            n_samples = int(n_samples)
            logger.info(f'Limiting the number of samples to: {n_samples:0,.0f}')
            dataset = dataset[:n_samples, :]
            targets = targets[:n_samples]
            logger.info(f'Triplet dataset now has {dataset.shape[0]:,d} samples and {dataset.shape[1]:d} features.')

        # performing the normalization/transformation
        logger.info('Performing normalization on:')
        for fdx, factor in enumerate(factors):
            feat_name = factor['column']
            feat_idx = feature2index[feat_name]
            factors[fdx]['source_feature_idx'] = fdx
            factors[fdx]['class'] = 'normalization'

            if factor['type'] == 'zscore':
                col_mean = np.mean(dataset[:, feat_idx])
                col_std = np.std(dataset[:, feat_idx])
                logger.info(f'{feat_name:>10}: type={factor["type"]}, mean={col_mean:8.1f}; std={col_std:8.1f}')
                dataset[:, feat_idx] = (dataset[:, feat_idx] - col_mean) / col_std
                factors[fdx]['mean'] = col_mean
                factors[fdx]['std'] = col_std
                factors[fdx]['id'] = f'{feat_name}:normalization:zscore:{fdx}'
            elif factor['type'] == 'none':
                pass
            else:
                raise ValueError(f'Unknown normalization/transformation method: {factor["type"]}')

        # constructing the KD-tree
        kdtree_time = time.time()
        logger.info('Constructing KDTree using the collected samples, shape=[{:,d} x {:,d}] ...'.format(*dataset.shape))
        kdtree = KDTree(dataset, leaf_size=50, metric='euclidean')
        logger.info('Finished in {:0.1f}s'.format(time.time() - kdtree_time))

        # produce a meta-data object
        hasher = hashlib.md5()
        hasher.update('\n'.join(triplets_obj.properties['triplix_headers']).encode())
        kdtree_metadata = dict(
            creation_timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
            triplix_version=configurations.configs['version'],
            source_hash=hasher.hexdigest(),
            source_header=triplets_obj.properties['triplix_headers'],
            n_sample=dataset.shape[0],
            n_feature=dataset.shape[1],
            factors_id=factors_id,
            factors=factors,
            feature2index=feature2index,
            target_name=target,
            target_values=targets,
        )

        # storing the KDTree object
        logger.info(f'Storing the KDTree in: {output_path}')
        joblib.dump({
            'kdtree': kdtree,
            'metadata': kdtree_metadata
        }, filename=output_path, protocol=-1, compress=('zlib', 2))
        logger.info(f'KDTree is stored successfully: file size={os.stat(output_path).st_size / 1e9:0,.1f}GB')

