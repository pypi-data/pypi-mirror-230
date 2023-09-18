# todo: find overlaps between fragments of a read and flag them accordingly

import time
import pathlib

import h5py
import pandas as pd
import numpy as np

from triplix.core import configurations
from triplix.core.hdf5 import DatasetIterator
from triplix.core.header import TriplixHeader
from triplix.core.bam import BAMReader
from triplix.core.utilities import generate_prog_id
from triplix._logging import get_logger

__version__ = '1.0.0'
COMMAND_NAME = 'triplix.concatemer'
COMMAND_ID = f'{COMMAND_NAME}>{generate_prog_id()}'
logger = get_logger(COMMAND_NAME)


class Concatemers(dict):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.options = {
        #     'display.min_rows': 5
        # }

    def __repr__(self):
        return '<Concatemers>\n' + repr(pd.DataFrame(self))

    def to_dataframe(self, *args, **kwargs):
        return pd.DataFrame(self, *args, **kwargs)


class ConcatemersContainer:

    def __init__(self, file_path):
        self.file_path = pathlib.Path(file_path).expanduser()
        assert self.file_path.is_file(), f'File not found: {file_path}'
        logger.debug(f'Opening (mode=r): {self.file_path}')
        self.h5_file = h5py.File(self.file_path, mode='r')

    def __len__(self):
        return self.h5_file['/reads/name'].shape[0]

    def iter(self, return_name=False, return_length=False):

        # initializing dataset iterators
        ds_iters = dict()
        for group_name in ['reads', 'concatemers']:
            ds_iters[group_name] = dict()
            for ds_name in self.h5_file[f'/{group_name}'].keys():
                ds_iters[group_name][ds_name] = DatasetIterator(self.h5_file, f'/{group_name}/{ds_name}')

        # iterate over concatemers/reads
        n_alignments = len(ds_iters['concatemers']['read_idx'])
        n_concatemers = len(self)
        start_idx = next(ds_iters['reads']['row_index'])
        for cctm_idx in range(n_concatemers):
            end_idx = next(ds_iters['reads']['row_index'], n_alignments)
            n_frag = end_idx - start_idx

            concatemer = Concatemers()
            for ds_name in ds_iters['concatemers'].keys():
                concatemer[ds_name] = ds_iters['concatemers'][ds_name].get_next(n_frag)

            if return_name:
                concatemer['read_name'] = ds_iters['reads']['name'].get_next(1)[0].decode()
            if return_length:
                concatemer['read_length'] = ds_iters['reads']['length'].get_next(1)[0]

            yield concatemer
            start_idx = end_idx

    def __getitem__(self, pointer):
        read_grp = self.h5_file[f'/reads']
        cctm_grp = self.h5_file[f'/concatemers']
        n_read = len(read_grp['row_index'])

        # calculate read start/end
        if isinstance(pointer, slice):
            if pointer.step is not None:
                raise NotImplementedError('Step argument is not supported.')
            if pointer.start is None:
                read_start = 0
            else:
                read_start = int(pointer.start)
            if pointer.stop is None:
                read_end = n_read
            else:
                read_end = int(pointer.stop)
        else:
            read_start = int(pointer)
            read_end = read_start + 1
        read_end = min(read_end, n_read)

        # calculate row start/end
        row_start = read_grp['row_index'][read_start]
        row_end = read_grp['row_index'][read_end]

        # load fragments columns
        concatemers = Concatemers()
        for ds_name in cctm_grp.keys():
            concatemers[ds_name] = cctm_grp[ds_name][row_start:row_end]

        # assign read columns
        read_names = np.array([name.decode() for name in read_grp['name'][read_start:read_end]])
        read_lengths = read_grp['length'][read_start:read_end]
        read_idxs = np.unique(concatemers['read_idx'], return_inverse=True)[1]
        concatemers['read_name'] = read_names[read_idxs]
        concatemers['read_length'] = read_lengths[read_idxs]

        return concatemers


class ExporterHDF5:

    def __init__(
            self, bam_path, assembly, output_dir=None,
            output_name=None, assume_sorted=False,
            cell_type=None, assay_name=None, experiment_name=None,
    ):

        self.assembly = assembly
        self.cell_type = cell_type
        self.assay_name = assay_name
        self.experiment_name = experiment_name
        if self.experiment_name is None:
            self.experiment_name = bam_path.stem

        bam_path = pathlib.Path(bam_path).expanduser()
        if output_dir is None:
            output_dir = bam_path.parent
        if output_name is None:
            output_name = self.experiment_name + '.concatemers.h5'
        self.output_path = pathlib.Path(output_dir).expanduser() / output_name
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        if self.output_path.is_file():
            self.output_path.unlink()

        # prepare the input BAM file
        self.bam_reader = BAMReader(file_path=bam_path)
        if not assume_sorted and self.bam_reader.file_handle.header['HD']['SO'] != 'queryname':
            logger.error('Input BAM file should be sorted by `read name`. Please use `samtools sort -n` to sort the BAM file first.')
            raise ValueError('BAM file is not sorted.')

        self.chrom_lengths = {'unmapped': 0}
        for chr_idx, chr_name in enumerate(self.bam_reader.chroms):
            self.chrom_lengths[chr_name] = self.bam_reader.chrom_sizes[chr_idx]

        self.chrom2idx = {chr_name: idx for idx, chr_name in enumerate(self.chrom_lengths)}
        chrom_dtype = h5py.enum_dtype(self.chrom2idx, basetype='int8')

        self.strand2num = {'+': 1, '-': -1, '*': 0}
        strand_dtype = h5py.enum_dtype(self.strand2num, basetype='int8')

        self.dataset_names, self.dataset_dtypes = zip(*[
            ('read_idx', 'uint32'),
            ('chrom_num', chrom_dtype),
            ('start', 'int64'),
            ('end', 'int64'),
            ('strand', strand_dtype),
            ('map_quality', 'uint8'),
            ('flag', 'uint16'),
            ('seq_start', 'uint32'),
            ('seq_end', 'uint32'),
        ])
        self.dataset_defaults = dict(
            maxshape=(None, ),
            chunks=(configurations.configs['concatemers']['hdf5_chunk_size'], ),
            compression="gzip",
            compression_opts=configurations.configs['concatemers']['compression_level'],
            # track_order=True,
        )

    def initialize_hdf5(self):
        logger.debug(f'Opening (mode=w): {self.output_path}')
        with h5py.File(self.output_path, mode='w') as h5_file:
            cnct_grp = h5_file.create_group('/concatemers', track_order=True)
            cnct_grp.attrs['format_version'] = __version__
            cnct_grp.attrs['software_version'] = configurations.configs['version']
            cnct_grp.attrs['creation_timestamp'] = time.strftime("%Y-%m-%d %H:%M:%S")
            cnct_grp.attrs['cell_type'] = self.cell_type
            cnct_grp.attrs['assay_name'] = self.assay_name
            cnct_grp.attrs['experiment_name'] = self.experiment_name
            cnct_grp.attrs['source_file'] = str(self.bam_reader.file_path)
            cnct_grp.attrs['assembly_name'] = self.assembly
            cnct_grp.attrs['assembly_length'] = sum(self.chrom_lengths.values())
            cnct_grp.attrs['chrom_names'] = list(self.chrom_lengths.keys())
            cnct_grp.attrs['chrom_lengths'] = list(self.chrom_lengths.values())
            cnct_grp.attrs['stored_chunks'] = [f'{chr_name}:0-{chr_end}' for chr_name, chr_end in self.chrom_lengths.items() if chr_name != 'unmapped']

            # adjust headers before inclusion
            headers = TriplixHeader(self.bam_reader.file_path)
            headers.process_history.add_pg(dict(ID=COMMAND_ID, PN=COMMAND_NAME, VN=configurations.configs['version'], PS=[headers.process_history.destination_id]))
            cnct_grp.attrs['sam_headers'] = headers.process_history.to_sam_headers()

            h5_file.create_group('/reads', track_order=True)

    def store_concatemers(self):
        read_names, read_lengths, concatemers_lst = [], [], []
        for read_idx, concatemer in enumerate(self.bam_reader.get_reads()):

            # filtering and sorting alignments
            #  256, 0x100: Not a primary alignment
            #  512, 0x200: Failed platform/vendor quality checks
            # 1024, 0x400: PCR or optical duplicate
            concatemer = filter(lambda aln: aln.flag & 0x700 == 0, concatemer)
            concatemer = sorted(concatemer, key=lambda aln: aln.seq_start)

            read_names.append(concatemer[0].read_name)
            read_lengths.append(concatemer[0].read_length)

            # append the batch if full
            concatemers_lst.extend(concatemer)
            if len(read_names) >= configurations.configs['concatemers']['batch_size']:
                logger.info(f'\tstoring concatemer #{read_idx + 1:,d} ...')
                self.append_to_hdf5(read_names, read_lengths, concatemers_lst)
                read_names, read_lengths, concatemers_lst = [], [], []

        if len(concatemers_lst) > 0:
            logger.info(f'\tstoring concatemer #{concatemers_lst[-1].read_idx + 1:,d} ...')
            self.append_to_hdf5(read_names, read_lengths, concatemers_lst)
        logger.info(f'In total, stored #{concatemers_lst[-1].read_idx + 1:,d} concatemers in: {self.output_path}')

    def append_to_hdf5(self, read_names, read_lengths, concatemers):
        ctime = time.time()

        concatemers = pd.DataFrame(concatemers)
        concatemers['chrom_num'] = concatemers['chrom'].map(self.chrom2idx)
        concatemers['strand'] = concatemers['strand'].map(self.strand2num)

        logger.debug(f'Opening (mode=a): {self.output_path}')
        with h5py.File(self.output_path, mode='a') as h5_file:

            read_grp = h5_file['/reads']
            cnct_grp = h5_file['/concatemers']
            row_indices = np.unique(concatemers['read_idx'], return_index=True)[1]
            if len(read_grp.keys()) == 0:  # no data is stored yet
                read_grp.create_dataset('row_index', data=row_indices, dtype='uint32', **self.dataset_defaults)
                read_grp.create_dataset('name', data=read_names, dtype=h5py.string_dtype(encoding='utf-8'), **self.dataset_defaults)
                read_grp.create_dataset('length', data=read_lengths, dtype='uint32', **self.dataset_defaults)

                for col_name, col_dtype in zip(self.dataset_names, self.dataset_dtypes):
                    cnct_grp.create_dataset(col_name, data=concatemers[col_name], dtype=col_dtype, **self.dataset_defaults)
                    if configurations.configs['debug']:
                        logger.debug(f'\tSize of "{col_name:20s}" is: {cnct_grp[col_name].nbytes / 1e6:0.2f}mb')
            else:

                # append to `reads` group
                n_cur = len(read_grp['name'])
                n_new = len(read_names)
                collection = {
                    'row_index': len(cnct_grp['start']) + row_indices,
                    'name': read_names,
                    'length': read_lengths,
                }
                for col_name in collection:
                    read_grp[col_name].resize(n_cur + n_new, axis=0)
                    read_grp[col_name][-n_new:] = collection[col_name]

                # append to `concatemers` group
                n_cur = len(cnct_grp['start'])
                n_new = len(concatemers)
                for col_name in self.dataset_names:
                    cnct_grp[col_name].resize(n_cur + n_new, axis=0)
                    cnct_grp[col_name][-n_new:] = concatemers[col_name]
        if configurations.configs['debug']:
            logger.debug(f'Stored this batch in: {time.time() - ctime:0.2f}s')
