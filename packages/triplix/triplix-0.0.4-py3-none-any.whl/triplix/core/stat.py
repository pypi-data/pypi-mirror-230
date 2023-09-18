
import time
import pathlib

import numpy as np
import h5py

from triplix.core import configurations
from triplix.core.concatemers import ConcatemersContainer
from triplix._logging import get_logger

COMMAND_NAME = 'triplix.stat'
logger = get_logger(COMMAND_NAME)


def collect_contact_decay_stats(concatemer_path, output_dir=None, output_name=None):
    source_path = pathlib.Path(concatemer_path).expanduser()

    # prepare output file
    if output_dir is None:
        output_dir = source_path.parent
    if output_name is None:
        output_name = source_path.name.replace('.concatemers.h5', '') + '.stats.h5'
    output_path = pathlib.Path(output_dir).expanduser() / output_name
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # prepare output options
    h5_defaults = dict(
        compression="gzip",
        compression_opts=configurations.configs['concatemers']['compression_level'],
    )

    # prepare the container
    cctm_container = ConcatemersContainer(source_path)
    concatemers_iter = cctm_container.iter(return_name=True, return_length=True)

    # criteria
    chrom_names = list(cctm_container.h5_file['concatemers'].attrs['chrom_names'])
    criteria = {
        'chrom_num': list(range(len(chrom_names))),
        'mapq': list(range(0, 60 + 1, 5)) + [np.inf],
        'cctm_n_chrom': list(range(0, 12 + 1)) + [np.inf],
        'cctm_n_frag': list(range(0, 12 + 1)) + [np.inf],
        'cctm_n_cis': list(range(0, 12 + 1)) + [np.inf],
    }
    bin_edges_lin = np.hstack([np.linspace(0, 9.5e3, 20, dtype=int), np.linspace(10e3, 0.5e6, 50, dtype=int), np.inf])
    bin_edges_log = np.hstack([0, 5000, np.logspace(4, 8, 37, base=10, dtype=int), np.inf])
    counts_lin = np.zeros([len(axis_edges) for axis_edges in criteria.values()] + [len(bin_edges_lin)], dtype=int)
    counts_log = np.zeros([len(axis_edges) for axis_edges in criteria.values()] + [len(bin_edges_log)], dtype=int)

    # iterate over concatemers
    logger.log_time = time.time()
    n_concatemer = cctm_container.h5_file['/reads/name'].shape[0]
    # n_alignment = len(cctm_container.h5_file['/concatemers/start'])
    logger.info(f'Iterating over {n_concatemer:,d} concatemers in: {concatemer_path}')
    for cnct_idx, concatemer in enumerate(concatemers_iter):
        if time.time() - logger.log_time > configurations.configs['log_interval']:
            logger.log_time = time.time()
            logger.info(f'\t{cnct_idx:,d}/{n_concatemer:,d} concatemers are processed. ')
        n_frag = len(concatemer['read_idx'])
        n_frag_idx = min(n_frag, len(criteria['cctm_n_frag']) - 1)

        # iterate over chromosomes
        captured_chrs, captured_freq = np.unique(concatemer['chrom_num'], return_counts=True)
        n_chrom = len(captured_chrs)
        n_chrom_idx = min(n_chrom, len(criteria['cctm_n_chrom']) - 1)
        captured_chrs = captured_chrs[captured_freq > 1]

        # iterate over chromosomes with multi-way captures
        for chrom_cis in captured_chrs:
            cis_idxs = np.where(concatemer['chrom_num'] == chrom_cis)[0]
            n_cis = len(cis_idxs)
            n_cis_idx = min(n_cis, len(criteria['cctm_n_cis']) - 1)

            for cis_idx_i in range(n_cis):
                for cis_idx_j in range(cis_idx_i + 1, n_cis):
                    fi = cis_idxs[cis_idx_i]
                    fj = cis_idxs[cis_idx_j]

                    contact_length = np.abs(concatemer['start'][fi] - concatemer['start'][fj])

                    min_mapq = min(concatemer['map_quality'][fi], concatemer['map_quality'][fj])
                    mapq_idx = np.searchsorted(criteria['mapq'], min_mapq, side='right') - 1

                    counts_lin[
                        chrom_cis,
                        mapq_idx,
                        n_chrom_idx,
                        n_frag_idx,
                        n_cis_idx,
                        np.searchsorted(bin_edges_lin, contact_length, side='right') - 1,
                    ] += 1
                    counts_log[
                        chrom_cis,
                        mapq_idx,
                        n_chrom_idx,
                        n_frag_idx,
                        n_cis_idx,
                        np.searchsorted(bin_edges_log, contact_length, side='right') - 1,
                    ] += 1
        # if cnct_idx > 500e3:
        #     break

    # prepare the output path
    logger.info(f'Storing contact counts in: {output_path}')
    logger.debug(f'Opening (mode=w): {output_path}')
    with h5py.File(output_path, mode='w') as h5_file:

        ds_axes = h5_file.create_dataset('axes', data=list(criteria.keys()), dtype=h5py.string_dtype(encoding='utf-8'), **h5_defaults)
        for ax_name, ax_edges in criteria.items():
            ds_axes.attrs[ax_name] = ax_edges

        ds_lin = h5_file.create_dataset('n_contacts_linear', data=counts_lin, dtype='uint32', **h5_defaults)
        ds_lin.attrs['bins'] = bin_edges_lin

        ds_log = h5_file.create_dataset('n_contacts_logarithmic', data=counts_log, dtype='uint32', **h5_defaults)
        ds_log.attrs['bins'] = bin_edges_log

    logger.info('All contact counts are stored successfully.')

