# todo: add an argument to ignore adding Triplets that are overlapping with each other within a read


import gzip
import pathlib
import copy
import time

import h5py
import numpy as np

from triplix.core import configurations
from triplix.core.header import TriplixHeader
from triplix.core.concatemers import ConcatemersContainer
from triplix.core.utilities import generate_prog_id
from triplix._logging import get_logger

# produce pairix:
# en=sample_100e3_0;
# pairtools parse --chroms-path=${HOME}/bulk/my_works/delaat_repositories/hic_processing/references/hg38.chrom.sizes.tsv --output=./pairs/${en}.parsed.pairsam.gz --add-columns mapq bams/${en}.bam
# pairtools sort --output=./pairs/${en}.sorted.pairsam.gz ./pairs/${en}.parsed.pairsam.gz
# pairtools merge --output=./pairs/sample_100e3.merged.gz ./pairs/*.sorted.pairsam.gz

FORMAT_VERSION = '1.0.0'
COMMAND_NAME = 'triplix.tri-alignment'
COMMAND_ID = f'{COMMAND_NAME}>{generate_prog_id()}'
logger = get_logger(COMMAND_NAME)


class TriAlignmentExtractor:
    def __init__(self, concatemers_path, output_dir=None, output_name=None):
        self.concatemers_path = pathlib.Path(concatemers_path).expanduser()
        self.header = TriplixHeader(file_path=concatemers_path)
        self.experiment_name = self.header.experiment_name

        if output_dir is None:
            output_dir = self.concatemers_path.parent
        if output_name is None:
            output_name = str(self.concatemers_path.name).replace('.concatemers.h5', '') + '.tri-alignments.tsv.bgz'
        self.output_path = pathlib.Path(output_dir).expanduser() / output_name
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

    def extract_tri_alignments(self):

        # initialize output files and add Triplix headers
        output_files = {}
        for chrom in self.header.chrom_lengths.keys():
            if chrom == 'unmapped':
                continue
            output_path = str(self.output_path).replace('.tri-alignments.tsv.bgz', f'.{chrom}.tri-alignments.tsv.bgz')
            logger.debug(f'Initializing output file: {output_path}')
            output_files[chrom] = gzip.open(output_path, 'wt', compresslevel=3)

            # include a PG header SAM headers to describe the Triplet generation procedure
            taln_header = copy.deepcopy(self.header)
            taln_header.stored_chunks = [(chrom, 0, self.header.chrom_lengths[chrom])]
            taln_header.process_history.add_pg(dict(ID=COMMAND_ID, PN=COMMAND_NAME, VN=configurations.configs['version'], PS=[taln_header.process_history.destination_id]))
            output_files[chrom].write(taln_header.to_string() + '\n')

        # get ENUM data mappers
        cctm_container = ConcatemersContainer(file_path=self.concatemers_path)
        chrom2num = h5py.check_enum_dtype(cctm_container.h5_file['/concatemers/chrom_num'].dtype)
        strnd2num = h5py.check_enum_dtype(cctm_container.h5_file['/concatemers/strand'].dtype)
        num2chrom = {value: key for key, value in chrom2num.items()}
        num2strnd = {value: key for key, value in strnd2num.items()}

        # iterate over concatemers
        logger.info(f'Extracting cis tri-alignments from each concatemer ...')
        concatemers_iter = cctm_container.iter(return_name=True, return_length=True)
        n_concatemer = cctm_container.h5_file['/reads/name'].shape[0]
        n_tri_alignments = 0
        logger.log_time = time.time()
        for cnct_idx, concatemer in enumerate(concatemers_iter):
            # pd.DataFrame(concatemer)
            if time.time() - logger.log_time > configurations.configs['log_interval']:
                logger.log_time = time.time()
                logger.info(f'\t{cnct_idx:,d}/{n_concatemer:,d} concatemers are processed. '
                            f'{n_tri_alignments:,d} tri-alignments are generated so far ...')
            n_frag = len(concatemer['read_idx'])

            # identify multi-way interactions
            captured_chrs, captured_freq = np.unique(concatemer['chrom_num'], return_counts=True)
            captured_chrs = captured_chrs[captured_freq > 2]

            # iterate over chromosomes with multi-way captures
            for ci, chrom_cis in enumerate(captured_chrs):
                cis_idxs = np.where(concatemer['chrom_num'] == chrom_cis)[0]
                n_cis = len(cis_idxs)
                cis_idxs = cis_idxs[np.argsort(concatemer['start'][cis_idxs])]

                # iterate over cis alignments
                for cis_idx_i in range(n_cis):
                    for cis_idx_j in range(cis_idx_i + 1, n_cis):
                        for cis_idx_k in range(cis_idx_j + 1, n_cis):
                            i = cis_idxs[cis_idx_i]
                            j = cis_idxs[cis_idx_j]
                            k = cis_idxs[cis_idx_k]

                            tri_alignment_str = (
                                    f"{num2chrom[concatemer['chrom_num'][i]]}\t{concatemer['start'][i]}\t{concatemer['end'][i]}\t"
                                    + f"{num2chrom[concatemer['chrom_num'][j]]}\t{concatemer['start'][j]}\t{concatemer['end'][j]}\t"
                                    + f"{num2chrom[concatemer['chrom_num'][k]]}\t{concatemer['start'][k]}\t{concatemer['end'][k]}\t"
                                    + f"{num2strnd[concatemer['strand'][i]]:s}\t"
                                    + f"{num2strnd[concatemer['strand'][j]]:s}\t"
                                    + f"{num2strnd[concatemer['strand'][k]]:s}\t"
                                    + f"{concatemer['map_quality'][i]:d}\t"
                                    + f"{concatemer['map_quality'][j]:d}\t"
                                    + f"{concatemer['map_quality'][k]:d}\t"
                                    + f"{i:d}\t"
                                    + f"{j:d}\t"
                                    + f"{k:d}\t"
                                    + f"{concatemer['read_name']:s}\t"
                                    + f"{concatemer['read_length']:d}\t"
                                    + f"{n_frag:d}\t"
                                    + f"{self.experiment_name:s}\n"
                            )
                            output_files[num2chrom[chrom_cis]].write(tri_alignment_str)
                            n_tri_alignments += 1
        logger.info(f'All {n_tri_alignments:,d} tri-alignments are exported successfully.')

        # closing the output file handles
        logger.info(f'Closing the output file handles:')
        for chrom, file_handle in output_files.items():
            file_handle.close()
            logger.debug(f'File closed: {file_handle.name}')

