import copy
import pathlib
import time
from typing import Any, Union, Iterable
# from collections import deque

import fasteners
import h5py
import numpy as np
import pandas as pd
from triplix.core import configurations
from triplix.core.hdf5 import HDF5Container
from triplix.core.header import TriplixHeader
from triplix.core.utilities import overlap, generate_prog_id, merge_intervals
from triplix._logging import get_logger

__version__ = '1.0.0'
COMMAND_NAME = 'triplix.triplets'
COMMAND_ID = f'{COMMAND_NAME}>{generate_prog_id()}'
logger = get_logger(COMMAND_NAME)


class Triplets(dict):

    def __init__(self, *args, **kwargs):
        columns = kwargs.pop('columns', [])

        # initialize the `dict` object
        super().__init__(*args, **kwargs)
        self.options = {
            'display.min_rows': 5
        }

        # initialize columns, if given
        for column in columns:
            self[column] = []

    def __repr__(self):
        # if 'start_A' not in self:
            # return '<Miss-formatted Triplets>: Missing `start_A` column'
        n_row = len(self)
        if n_row == 0:
            return f'--- Empty Triplets ---'
        
        n_show = self.options['display.min_rows']
        if n_row <= n_show:
            show_df = pd.DataFrame(self).astype(str)
        else:
            show_idxs = list(range(0, n_show + 1)) + list(range(n_row - n_show, n_row))
            show_df = pd.DataFrame({key: np.array(values)[show_idxs] for (key, values) in self.items()}, index=show_idxs)
            show_df = show_df.astype(str)
            show_df.loc[n_show, :] = '***'
            show_df.index = show_df.index.astype(str)
            show_df.rename({str(n_show): '***'}, axis=0, inplace=True)
        return f'Triplets <{n_row} x {len(self.keys())}>:\n' + repr(show_df)

    def __len__(self):
        for column in self.keys():
            return len(self[column])
        return 0

    def __getitem__(self, pointer: Union[str, slice, int, Iterable]):
        if isinstance(pointer, str):  # we are requesting a key/column of the parent dict object
            return dict.__getitem__(self, pointer)

        out = Triplets()
        for col in self.keys():
            array = np.array(dict.__getitem__(self, col))

            # selecting the requested rows
            if isinstance(pointer, (slice, )):
                out[col] = array[pointer]
            elif hasattr(pointer, '__iter__'):  # or more specifically: isinstance(pointer, (list, pd.Series, np.ndarray))
                out[col] = array[pointer]
            elif isinstance(pointer, int):
                out[col] = [array[pointer]]
            else:
                raise ValueError(f'Unknown index type: {pointer}')
        return out

    def clear(self):
        for column in self.keys():
            self[column] = []

    def to_dataframe(self, *args, **kwargs):
        return pd.DataFrame(self, *args, **kwargs)

    def to_slice(self, view_point, anchor_edges, value_column='count_ABC', symmetric=True):

        # find viewpoint's index
        vp_idx = np.searchsorted(anchor_edges, view_point, side='right') - 1
        anchor_idxs = np.searchsorted(anchor_edges, [
            self['start_A'],
            self['start_B'],
            self['start_C']
        ], side='right').T - 1

        # sort indices relative to viewpoint
        vp_dist = np.abs(anchor_idxs - vp_idx)
        sorted_idxs = np.take_along_axis(anchor_idxs, np.argsort(vp_dist, axis=1), axis=1)

        # find triplets having a viewpoint
        n_anchor = len(anchor_edges) - 1
        has_vp = sorted_idxs[:, 0] == vp_idx
        is_valid = (
            has_vp &
            (anchor_idxs >= 0).all(axis=1) &
            (anchor_idxs < n_anchor).all(axis=1)
        )

        # populate the map
        slice_map = np.full([n_anchor, n_anchor], fill_value=np.nan)
        slice_map[sorted_idxs[is_valid, 1], sorted_idxs[is_valid, 2]] = self[value_column][is_valid]
        if symmetric:
            slice_map[sorted_idxs[is_valid, 2], sorted_idxs[is_valid, 1]] = self[value_column][is_valid]

        return slice_map

    def to_cube(self, anchor_edges, value_column='count_ABC'):

        # find triplets overlapping the given anchor_edges
        anchor_idxs = np.searchsorted(anchor_edges, [self['start_A'], self['start_B'], self['start_C']], side='right').T - 1
        n_anchor = len(anchor_edges) - 1
        is_valid = (
                np.all(anchor_idxs >= 0, axis=1) &
                np.all(anchor_idxs < n_anchor, axis=1)
        )

        # populate the cube of counts
        cube_map = np.full([n_anchor, n_anchor, n_anchor], fill_value=np.nan)
        cube_map[
            anchor_idxs[is_valid, 0],
            anchor_idxs[is_valid, 1],
            anchor_idxs[is_valid, 2]
        ] = self[value_column]

        return cube_map

    def sort_anchors(self, by, force_upper=True):
        by = int(by)
        triplets = copy.deepcopy(self)

        sorted_idxs = None
        for anchor_type in ['start', 'end']:
            if f'{anchor_type}_A' not in triplets:
                continue
            coords = np.array([
                triplets[f'{anchor_type}_A'],
                triplets[f'{anchor_type}_B'],
                triplets[f'{anchor_type}_C'],
            ], dtype=int).T
            if anchor_type == 'start':
                anchor_distance = np.abs(coords - by)
                sorted_idxs = np.argsort(anchor_distance, axis=1)

            sorted_coords = np.take_along_axis(coords, sorted_idxs, axis=1)
            triplets[f'{anchor_type}_A'] = sorted_coords[:, 0]
            triplets[f'{anchor_type}_B'] = sorted_coords[:, 1]
            triplets[f'{anchor_type}_C'] = sorted_coords[:, 2]

        if force_upper:
            is_tril = triplets['start_B'] > triplets['start_C']
            if np.any(is_tril):
                triplets['start_B'][is_tril], triplets['start_C'][is_tril] = triplets['start_C'][is_tril], triplets['start_B'][is_tril]
                if 'end_B' in triplets:
                    triplets['end_B'][is_tril], triplets['end_C'][is_tril] = triplets['end_C'][is_tril], triplets['end_B'][is_tril]

        return triplets


class TripletsContainer:

    def __init__(self, container_path, tri_alignments_path=None, anchor_width=None, anchor_max_distance=None, exclusive=False, auto_init=False):
        self.container_path = pathlib.Path(container_path).expanduser()
        self.dataset_defaults = dict(
            maxshape=(None,),
            chunks=(configurations.configs['triplets']['hdf5_chunk_size'],),
            compression="gzip",
            compression_opts=configurations.configs['triplets']['compression_level'],
        )

        # prepare the lock
        self.lock_handle = fasteners.InterProcessLock(f'{self.container_path}.lock')
        self.exclusive = exclusive

        # check if the container needs initialization
        self.properties = {}
        if auto_init:
            logger.debug(f'Checking if the container is present: {self.container_path}')
            self.lock()
            if self.container_path.is_file():
                logger.debug('The input Triplets container is present. There is no need for initialization.')
            else:
                logger.debug('No Triplet container is found. Initializing the container.')
                assert tri_alignments_path is not None, 'When initializing the container, `tri_alignments_path` argument is required.'
                assert anchor_width is not None, 'When initializing the container, `anchor_width` argument is required.'
                assert anchor_max_distance is not None, 'When initializing the container, `anchor_max_distance` argument is required.'
                self.properties = {
                    'anchor_max_distance': int(anchor_max_distance),
                    'anchor_width': int(anchor_width),
                }
                self.initialize_container(tri_alignments_path=tri_alignments_path, exclusive=False)
            self.unlock()

        # collect experiment properties
        logger.debug('Collecting experiment properties')
        self.fetch_properties(exclusive=True)  # should be exclusive, otherwise it fails when multiple process is reading from it
        # one solution could be: https://stackoverflow.com/questions/68457924/error-while-accessing-hdf5-file-shows-error-oserror-unable-to-open-file
        self.experiment_path = f'experiments/{self.properties["experiment_name"]}/'

        if anchor_width is not None:
            assert self.properties['anchor_width'] == anchor_width, f'Inconsistent argument: `anchor_width`={anchor_width}'
        if anchor_max_distance is not None:
            assert self.properties['anchor_max_distance'] == anchor_max_distance, f'Inconsistent argument: `anchor_max_distance`={anchor_max_distance}'
        if self.properties['storage_format'] != 'full':
            raise NotImplementedError('Only "full" storage format is supported')
        if self.properties['anchor_type'] != 'fixed':
            raise NotImplementedError('Only fixed-width anchors is supported')

        if self.exclusive:
            self.lock()

    def __enter__(self):
        return self
    
    def __exit__(self, exception_type, exception_value, exception_traceback):
        if self.exclusive:
            self.unlock()
    
    def iter_chunks(self, chroms=None, columns=None):
        if chroms is None:
            chroms = self.properties['chrom_names']
        if columns is None:
            columns = self.properties['columns_order']
        if not isinstance(chroms, list):
            chroms = [chroms]
        if not isinstance(columns, list):
            columns = [columns]

        with HDF5Container(self.container_path, mode='r', exclusive=False) as container:
            for chrom in chroms:
                cis_path = f'{self.experiment_path}/contacts/triplets/{chrom},{chrom},{chrom}'
                if cis_path not in container.h5_file:
                    continue
                
                # preparing a chunk iterator
                cis_group = container.h5_file[cis_path]
                ds_slicer = cis_group[columns[0]].iter_chunks()
                
                # iterating over chunks
                triplets = Triplets()
                while True:
                    try:
                        ds_slice = next(ds_slicer)
                        for column in columns:
                            triplets[column] = cis_group[column][ds_slice]
                        yield chrom, triplets
                    except StopIteration:
                        break
    
    def to_dataframe(self, *args, **kwargs):
        return pd.DataFrame(self, *args, **kwargs)
    
    def lock(self):
        logger.debug(f'Requesting (an exclusive) right to: {self.container_path}')
        self.lock_handle.acquire()
        logger.debug(f'Permission acquired: {self.container_path}')

    def unlock(self):
        self.lock_handle.release()
        lock_path = self.lock_handle.path.decode()
        # pathlib.Path(lock_path).unlink()
        logger.debug(f'Container lock is released: {lock_path}')

    def initialize_container(self, tri_alignments_path, exclusive=True):
        trialn_header = TriplixHeader(file_path=tri_alignments_path)
        anchor_width = self.properties['anchor_width']
        anchor_max_distance = self.properties['anchor_max_distance']

        with HDF5Container(self.container_path, mode='w', exclusive=exclusive) as container:

            # experiment attributes
            expr_grp = container.h5_file.create_group(f'/experiments/{trialn_header.experiment_name}')  # , track_order=True: keep False, because of https://github.com/h5py/h5py/issues/1385
            expr_grp.attrs['format'] = 'HDF5::Triplix_Triplets'
            expr_grp.attrs['format_version'] = __version__
            expr_grp.attrs['triplix_version'] = configurations.configs['version']
            expr_grp.attrs['creation_timestamp'] = time.strftime("%Y-%m-%d %H:%M:%S")
            expr_grp.attrs['assembly_name'] = trialn_header.assembly_name
            expr_grp.attrs['assembly_length'] = sum(trialn_header.chrom_lengths.values())
            if trialn_header.assay_name is not None:
                expr_grp.attrs['assay_name'] = trialn_header.assay_name
            else:
                expr_grp.attrs['assay_name'] = 'unknown'
            if trialn_header.cell_type is not None:
                expr_grp.attrs['cell_type'] = trialn_header.cell_type
            else:
                expr_grp.attrs['cell_type'] = 'unknown'
            expr_grp.attrs['experiment_name'] = trialn_header.experiment_name
            expr_grp.attrs['source_bam_file'] = str(trialn_header.source_file)
            expr_grp.attrs['storage_format'] = 'full'  # {'full', 'sparse'}
            expr_grp.attrs['storage_mode'] = 'symmetric, upper triangle'  # { "symmetric, upper triangle", "square" }
            expr_grp.attrs['anchor_type'] = 'fixed'  # { "fixed", "variable" }
            expr_grp.attrs['anchor_width'] = int(anchor_width)
            expr_grp.attrs['anchor_max_distance'] = int(anchor_max_distance)
            expr_grp.attrs['user_metadata'] = '{}'
            if expr_grp.attrs['storage_format'] != 'full':
                raise NotImplementedError('Only "full" storage format is supported')
            if expr_grp.attrs['anchor_type'] != 'fixed':
                raise NotImplementedError('Only fixed-width anchor is supported')

            # add meta-data group
            trialn_header.update(
                creation_timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
                format_version=TriplixHeader.FORMAT_VERSION,
                anchor_width=anchor_width,
                column_names=[],
            )
            meta_grp = expr_grp.create_group(f'metadata/')
            meta_grp.create_dataset(name='triplix_headers', data=trialn_header.to_string().split('\n'), dtype=h5py.string_dtype(encoding='utf-8'), **self.dataset_defaults)
            meta_grp.create_dataset(name='sam_headers', data=trialn_header.process_history.to_sam_headers(), dtype=h5py.string_dtype(encoding='utf-8'), **self.dataset_defaults)

            chnk_grp = meta_grp.create_group(name='stored_chunks')
            chnk_grp.create_dataset(name='chrom', data=[], dtype=h5py.string_dtype(encoding='utf-8'), **self.dataset_defaults)
            chnk_grp.create_dataset(name='start', data=[], dtype='uint32', **self.dataset_defaults)
            chnk_grp.create_dataset(name='end', data=[], dtype='uint32', **self.dataset_defaults)

            # add chromosome group
            chrom_grp = expr_grp.create_group(f'chroms/')
            chrom_grp.create_dataset(name='name', data=list(trialn_header.chrom_lengths.keys()), dtype=h5py.string_dtype(encoding='utf-8'), **self.dataset_defaults)
            chrom_grp.create_dataset(name='length', data=list(trialn_header.chrom_lengths.values()), dtype='uint32', **self.dataset_defaults)

            # add a contacts/triplets group to store the cis-triplets
            cnct_grp = expr_grp.create_group(f'contacts/')
            trpl_grp = cnct_grp.create_group('triplets')
            trpl_grp.attrs['columns_order'] = [
                'flag',
                'start_A', 'start_B', 'start_C',
                'distance_AB', 'distance_AC', 'distance_BC',
                'count_A', 'count_B', 'count_C',
                'count_AB', 'count_AC', 'count_BC',
                'count_ABC',
            ]

            # iterate over each chrom, add anchors and triplets
            for chr_idx, (chrom_name, chrom_length) in enumerate(trialn_header.chrom_lengths.items()):
                if chrom_name == 'unmapped':
                    continue
                logger.debug(f'Initializing contact dataset: {chrom_name}')

                # define anchors
                anchor_edges = np.arange(0, chrom_length + anchor_width, anchor_width, dtype=int)
                ancr_grp = cnct_grp.create_group(f'anchors/{chrom_name}/')
                ancr_grp.create_dataset(name='start', data=anchor_edges[:-1], dtype='uint32', **self.dataset_defaults)
                ancr_grp.create_dataset(name='end', data=anchor_edges[1:], dtype='uint32', **self.dataset_defaults)

                # pairs group, to store 2D data
                # todo: to be added later, to support storage of 2D data

                # prepare cis-contact group
                cis_grp = trpl_grp.create_group(f'{chrom_name},{chrom_name},{chrom_name}/')
                n_anchor = len(anchor_edges) - 1
                n_anchor_per_slice = anchor_max_distance // anchor_width + 1
                n_pairs_per_slice = int((n_anchor_per_slice + 1) * n_anchor_per_slice / 2)
                n_triplets = n_anchor * n_pairs_per_slice

                # prepare the coordinates
                start_a, start_b, start_c = self.index2pos(range(n_triplets))

                # set flag, range=[0x0000 - 0xffff]
                # 0x0000: No flag is set
                # 0x0001: The Triplet coordinate is out of chromosome interval
                # 0x0002: At least one Triplet has an unassigned column/dataset
                is_out_of_bound = (start_a > chrom_length) | (start_b > chrom_length) | (start_c > chrom_length)
                flag = (
                        is_out_of_bound * 1
                        + np.ones(n_triplets) * 2
                ).astype('uint16')
                cis_grp.create_dataset(name='flag', shape=(n_triplets,), data=flag, dtype='uint16', **self.dataset_defaults)

                # triplets
                # todo: to be added later: To support sparse CSR storage
                # trp_grp.create_dataset(name='index_A', shape=(n_triplets, ), dtype='uint32', **self.dataset_defaults)
                # trp_grp.create_dataset(name='index_B', shape=(n_triplets, ), dtype='uint32', **self.dataset_defaults)
                # trp_grp.create_dataset(name='index_C', shape=(n_triplets, ), dtype='uint32', **self.dataset_defaults)
                cis_grp.create_dataset(name='start_A', shape=(n_triplets,), data=start_a, dtype='uint32', **self.dataset_defaults)
                cis_grp.create_dataset(name='start_B', shape=(n_triplets,), data=start_b, dtype='uint32', **self.dataset_defaults)
                cis_grp.create_dataset(name='start_C', shape=(n_triplets,), data=start_c, dtype='uint32', **self.dataset_defaults)
                cis_grp.create_dataset(name='distance_AB', shape=(n_triplets,), dtype='uint32', **self.dataset_defaults)
                cis_grp.create_dataset(name='distance_AC', shape=(n_triplets,), dtype='uint32', **self.dataset_defaults)
                cis_grp.create_dataset(name='distance_BC', shape=(n_triplets,), dtype='uint32', **self.dataset_defaults)
                cis_grp.create_dataset(name='count_A', shape=(n_triplets,), dtype='uint32', **self.dataset_defaults)
                cis_grp.create_dataset(name='count_B', shape=(n_triplets,), dtype='uint32', **self.dataset_defaults)
                cis_grp.create_dataset(name='count_C', shape=(n_triplets,), dtype='uint32', **self.dataset_defaults)
                cis_grp.create_dataset(name='count_AB', shape=(n_triplets,), dtype='uint32', **self.dataset_defaults)
                cis_grp.create_dataset(name='count_AC', shape=(n_triplets,), dtype='uint32', **self.dataset_defaults)
                cis_grp.create_dataset(name='count_BC', shape=(n_triplets,), dtype='uint32', **self.dataset_defaults)
                cis_grp.create_dataset(name='count_ABC', shape=(n_triplets,), dtype='uint32', **self.dataset_defaults)
                del start_a, start_b, start_c

    def pos2index(self, pos_a, pos_b, pos_c):
        if not isinstance(pos_a, np.ndarray):
            pos_a = np.array(pos_a)
        if not isinstance(pos_b, np.ndarray):
            pos_b = np.array(pos_b)
        if not isinstance(pos_c, np.ndarray):
            pos_c = np.array(pos_c)
        pos_a = pos_a.astype(int)
        pos_b = pos_b.astype(int)
        pos_c = pos_c.astype(int)
        assert np.all(pos_a <= pos_b)
        assert np.all(pos_b <= pos_c)

        dist_ab = pos_b - pos_a
        dist_ac = pos_c - pos_a
        dist_bc = pos_c - pos_b
        assert np.all((dist_ab >= 0) & (dist_ab <= self.properties['anchor_max_distance']))
        assert np.all((dist_ac >= 0) & (dist_ac <= self.properties['anchor_max_distance']))
        assert np.all((dist_bc >= 0) & (dist_bc <= self.properties['anchor_max_distance']))

        index_a = pos_a // self.properties['anchor_width']
        index_b = pos_b // self.properties['anchor_width'] - index_a
        index_c = pos_c // self.properties['anchor_width'] - index_a

        n_anchors_per_slice = self.properties['anchor_max_distance'] // self.properties['anchor_width'] + 1
        n_pairs_per_slice = int((n_anchors_per_slice + 1) * n_anchors_per_slice / 2)
        n_pairs_skipped = (index_b * (index_b + 1) / 2).astype(int)

        ds_row_index = index_a * n_pairs_per_slice + n_anchors_per_slice * index_b + index_c - n_pairs_skipped
        return ds_row_index

    def index2pos(self, ds_row_index):
        n_anchor_per_window = self.properties['anchor_max_distance'] // self.properties['anchor_width'] + 1
        n_pairs_per_window = int((n_anchor_per_window + 1) * n_anchor_per_window / 2)

        index_a, index_window = np.divmod(ds_row_index, n_pairs_per_window)
        index_b = n_anchor_per_window - 1 - np.floor((-1 + np.sqrt((2 * n_anchor_per_window + 1) ** 2 - 8 * (index_window + 1))) / 2).astype(int)
        index_c = index_window - index_b * (2 * n_anchor_per_window - index_b - 1) // 2

        return (
            index_a * self.properties['anchor_width'],
            index_a * self.properties['anchor_width'] + index_b * self.properties['anchor_width'],
            index_a * self.properties['anchor_width'] + index_c * self.properties['anchor_width'],
        )

    def create_columns(self, triplets_path, col_names, dtype='float32', exclusive=True):
        with HDF5Container(self.container_path, mode='a', exclusive=exclusive) as container:
            self.fetch_properties(exclusive=False)
            columns_order = list(self.properties['columns_order'])
            trpl_grp = container.h5_file[triplets_path]
            cis_chrom_names = list(trpl_grp.keys())

            # add each column, if not present
            h5_modified = False
            for col_name in col_names:
                if col_name not in columns_order:
                    logger.debug(f'Adding "{col_name}" column to Triplet\'s `column_order`')
                    columns_order.append(col_name)
                    h5_modified = True

                    # add the column to each cis_contact
                    for cis_chrom_name in cis_chrom_names:
                        cnct_grp = trpl_grp[cis_chrom_name]

                        # determine number of rows
                        stored_columns = list(cnct_grp.keys())
                        n_row = cnct_grp[stored_columns[0]].shape[0]

                        # adding dataset
                        logger.debug(f'Adding "{col_name}" dataset to: {cnct_grp.name}')
                        if col_name in cnct_grp:
                            logger.warning(f'"{col_name}" already exists in "{cnct_grp}"')
                            continue
                        cnct_grp.create_dataset(name=col_name, shape=(n_row,), dtype=dtype, **self.dataset_defaults)

            # update the related variables
            if h5_modified:

                # set the flag column to "unassigned"
                for cis_chrom_name in cis_chrom_names:
                    logger.debug(f'Setting "flag" column of "{cis_chrom_name}" triplets as: Unassigned')
                    trpl_grp[cis_chrom_name]['flag'][:] = np.bitwise_or(trpl_grp[cis_chrom_name]['flag'], 0x0002)

                # update meta-data
                logger.debug(f'Updating column-order as: {columns_order}')
                self.properties['columns_order'] = columns_order
                self.properties['stored_chunks'] = []
                self.store_properties(exclusive=False)

    def drop_columns(self, columns, exclusive=True):
        assert isinstance(columns, list), f'Please provide a list of column names. Currently given: {columns}'

        with HDF5Container(self.container_path, mode='a', exclusive=exclusive) as container:
            self.fetch_properties(exclusive=False)
            columns_order = list(self.properties['columns_order'])
            experiment_name = self.properties['experiment_name']
            cis_grp = container.h5_file['experiments'][experiment_name]['contacts']['triplets']

            # iterate over each given column
            for col_name in columns:
                for cis_chrom in cis_grp.keys():
                    trpt_grp = cis_grp[cis_chrom]
                    if col_name not in trpt_grp:
                        logger.warning(f'Could not find "{col_name}" column in: {cis_chrom}')
                    else:
                        logger.debug(f'Removing "{col_name}" column from: {cis_chrom}')
                        del trpt_grp[col_name]
                if col_name in columns_order:
                    logger.debug(f'Deleting "{col_name}" item from `columns_order` metadata')
                    columns_order.remove(col_name)

            # updating the meta-data
            logger.debug(f'Updating column-order as: {columns_order}')
            self.properties['columns_order'] = columns_order
            self.store_properties(exclusive=False)

    def store(
            self, triplets,
            chrom_a, chrom_b=None, chrom_c=None,
            start_a=None, start_b=None, start_c=None,
            exclusive=True, verify_coords=False
    ):

        # initialization
        if chrom_b is None:
            chrom_b = chrom_a
        if chrom_c is None:
            chrom_c = chrom_b
        if start_a is None:  # get coordinates from the Triplet container itself
            assert start_b is None
            assert start_c is None
            start_a = triplets['start_A']
            start_b = triplets['start_B']
            start_c = triplets['start_C']

        # store the values in columns
        with HDF5Container(self.container_path, mode='a', exclusive=exclusive) as container:

            # add columns if needed
            triplets_path = self.experiment_path + f'/contacts/triplets/'
            self.create_columns(triplets_path=triplets_path, col_names=list(triplets.keys()), exclusive=False)

            # storing the data
            row_indices = self.pos2index(start_a, start_b, start_c)
            cis_path = self.experiment_path + f'/contacts/triplets/{chrom_a},{chrom_b},{chrom_c}/'
            for col_name, col_values in triplets.items():
                if verify_coords and col_name.startswith('start_'):
                    assert np.array_equal(
                        container.retrieve(dataset_path=cis_path + col_name, row_indices=row_indices, exclusive=False),
                        col_values,
                    )
                else:
                    container.store(dataset_path=cis_path + col_name, row_indices=row_indices, values=col_values, exclusive=False)

            # set valid flag for stored triplets
            if 'flag' in container.h5_file[cis_path]:
                logger.debug(f'Setting the "flag" column of {len(row_indices):,d} stored triplets to: "Assigned"')
                flags = container.retrieve(dataset_path=f'{cis_path}/flag', row_indices=row_indices, exclusive=False)
                flags = np.bitwise_and(flags, 0xffff - 0x0002)
                container.store(dataset_path=f'{cis_path}/flag', row_indices=row_indices, values=flags, exclusive=False)
                del flags

    def fetch(
            self,
            chrom_a, start_a, end_a,
            chrom_b=None, start_b=None, end_b=None,
            chrom_c=None, start_c=None, end_c=None,
            exclusive=True, columns=None,
    ):

        # sanity checks
        if chrom_b is None:
            chrom_b = chrom_a
        if chrom_c is None:
            chrom_c = chrom_b
        if start_b is None:
            start_b = start_a
        if start_c is None:
            start_c = start_b
        if end_b is None:
            end_b = end_a + self.properties['anchor_max_distance']
        if end_c is None:
            end_c = end_a + self.properties['anchor_max_distance']
        assert isinstance(chrom_a, str) and len(chrom_a) > 0
        assert isinstance(chrom_b, str) and len(chrom_b) > 0
        assert isinstance(chrom_c, str) and len(chrom_c) > 0

        # determine row_indices
        start_idx = self.pos2index(start_a, start_b, start_c)
        end_idx = self.pos2index(end_a, end_b, end_c)
        assert start_idx <= end_idx
        row_indices = np.arange(start_idx, end_idx + 1)

        # prepare the container loader
        with HDF5Container(self.container_path, mode='r', exclusive=exclusive) as container:
            cis_path = f'{self.experiment_path}/contacts/triplets/{chrom_a},{chrom_b},{chrom_c}'
            if columns is None:
                columns = self.properties['columns_order']

            # iteratively load datasets
            triplets = Triplets()
            for col_name in columns:
                triplets[col_name] = container.retrieve(dataset_path=f'{cis_path}/{col_name}', row_indices=row_indices, exclusive=False)

            # get "flag" columns
            if 'flag' in triplets:
                flags = triplets['flag']
            else:
                flags = container.retrieve(dataset_path=f'{cis_path}/flag', row_indices=row_indices, exclusive=False)

        # filter the collected triplets, to overlap with the chromosome interval and the requested range
        within_chrom = np.bitwise_and(flags, 0x0001) != 0x0001
        within_interval = (
            (overlap(query_start=start_a, query_end=end_a, ref_start=triplets['start_A'], ref_end=triplets['start_A'] + self.properties['anchor_width'])) &
            (overlap(query_start=start_b, query_end=end_b, ref_start=triplets['start_B'], ref_end=triplets['start_B'] + self.properties['anchor_width'])) &
            (overlap(query_start=start_c, query_end=end_c, ref_start=triplets['start_C'], ref_end=triplets['start_C'] + self.properties['anchor_width']))
        )
        is_valid = within_chrom & within_interval
        if not is_valid.all():
            triplets = triplets[is_valid]
        del flags, within_chrom, within_interval, is_valid

        # prepare the return data
        return triplets

    def store_properties(self, exclusive=True):
        with HDF5Container(self.container_path, mode='a', exclusive=exclusive) as container:
            expr_grp = container.h5_file[self.experiment_path]
            for prop_name, prop_value in self.properties.items():
                if prop_name == 'stored_chunks':
                    if len(self.properties['stored_chunks']) == 0:
                        chunks_chrom, chunks_start, chunks_end = [], [], []
                    else:
                        chunks_chrom, chunks_start, chunks_end = zip(*self.properties['stored_chunks'])

                    del expr_grp[f'metadata/stored_chunks']
                    chk_grp = expr_grp.create_group(name='metadata/stored_chunks/')
                    chk_grp.create_dataset(name='chrom', data=chunks_chrom, dtype=h5py.string_dtype(encoding='utf-8'), **self.dataset_defaults)
                    chk_grp.create_dataset(name='start', data=chunks_start, dtype='uint32', **self.dataset_defaults)
                    chk_grp.create_dataset(name='end', data=chunks_end, dtype='uint32', **self.dataset_defaults)
                elif prop_name == 'chrom_names':
                    del expr_grp['chroms/name']
                    expr_grp['chroms'].create_dataset(name='name', data=prop_value, dtype=h5py.string_dtype(encoding='utf-8'), **self.dataset_defaults)
                elif prop_name == 'chrom_lengths':
                    del expr_grp['chroms/length']
                    expr_grp['chroms'].create_dataset(name='length', data=prop_value, dtype='uint32', **self.dataset_defaults)
                elif prop_name in ['sam_headers', 'triplix_headers']:
                    del expr_grp[f'metadata/{prop_name}']
                    expr_grp['metadata'].create_dataset(name=prop_name, data=prop_value, dtype=h5py.string_dtype(encoding='utf-8'), **self.dataset_defaults)
                elif prop_name == 'columns_order':
                    expr_grp['contacts/triplets'].attrs['columns_order'] = prop_value
                else:
                    expr_grp.attrs[prop_name] = prop_value

    def fetch_properties(self, exclusive=True):
        with HDF5Container(self.container_path, mode='r', exclusive=exclusive) as container:
            experiments = list(container.h5_file[f'/experiments'].keys())
            if len(experiments) > 1:
                raise NotImplementedError('Only single-experiment Triplet files are supported')
            experiment_name = experiments[0]
            expr_grp = container.h5_file[f'/experiments/{experiment_name}']

            # get experiment's metadata
            self.properties['sam_headers'] = [header.decode() for header in expr_grp['metadata/sam_headers'][()]]
            self.properties['triplix_headers'] = [header.decode() for header in expr_grp['metadata/triplix_headers'][()]]

            # collect stored chunks
            chnk_grp = expr_grp['metadata/stored_chunks/']
            chunks_chrom = [chr_name.decode() for chr_name in chnk_grp['chrom']]
            chunks_start = chnk_grp['start'][()]
            chunks_end = chnk_grp['end'][()]
            self.properties['stored_chunks'] = [[chrom, start, end] for chrom, start, end in zip(chunks_chrom, chunks_start, chunks_end)]

            # get experiment's attributes
            for attr_name in expr_grp.attrs.keys():
                self.properties[attr_name] = expr_grp.attrs[attr_name]

            # get columns order
            self.properties['columns_order'] = list(expr_grp['contacts/triplets'].attrs['columns_order'])

            # further processing of attributes
            self.properties['chrom_names'] = [chr_name.decode() for chr_name in expr_grp['chroms/name']]
            self.properties['chrom_lengths'] = list(expr_grp['chroms/length'])

    def store_attribute(self, dataset_path: str, name: str, value: Any, exclusive=True):
        with HDF5Container(self.container_path, mode='a', exclusive=exclusive) as container:
            ds = container.h5_file[dataset_path]
            ds.attrs[name] = value

    def add_stored_chunk(self, chunk, exclusive=True):
        if exclusive:
            self.lock()
        logger.debug(f'Adding to stored chunks: {chunk}')

        self.fetch_properties(exclusive=False)
        stored_chunks = list(self.properties['stored_chunks'])
        stored_chunks.append(chunk)
        chunks_merged = merge_intervals(
            intervals=stored_chunks,
            chroms_order=self.properties['chrom_names']
        )
        self.properties['stored_chunks'] = chunks_merged
        self.store_properties(exclusive=False)

        if exclusive:
            self.unlock()

