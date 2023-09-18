
import pathlib
from typing import Union

import h5py
import fasteners
import numpy as np

from triplix.core import configurations
from triplix._logging import get_logger

COMMAND_NAME = 'triplix.hdf5'
logger = get_logger(COMMAND_NAME)


class DatasetIterator:

    def __init__(self, hdf5_path: Union[str, h5py.File], dataset_path):
        if isinstance(hdf5_path, h5py.File):
            self.h5_handle = hdf5_path
            logger.debug(f'Using the provided file handle: {self.h5_handle}')
        else:
            self.hdf5_path = pathlib.Path(hdf5_path).expanduser()
            assert self.hdf5_path.is_file(), f'File not found: {self.hdf5_path}'
            logger.debug(f'Opening (mode=r): {self.hdf5_path}')
            self.h5_handle = h5py.File(self.hdf5_path, mode='r')

        logger.debug(f'Selected dataset is: {dataset_path}')
        self.dataset = self.h5_handle[dataset_path]
        self.dataset_path = dataset_path
        self.dataset_iter_chunks = self.dataset.iter_chunks()
        self.data = self.dataset[next(self.dataset_iter_chunks)]
        self.offset = 0
        self.cursor = 0

    def get_next(self, n_items=1):

        # do we have enough loaded data?
        while self.cursor + n_items > len(self.data):

            # delete old (used) data
            if self.cursor != 0:
                self.data = self.data[self.cursor:]
                self.offset += self.cursor
                self.cursor = 0

            # collect new chunk of data
            try:
                chunk_slice = next(self.dataset_iter_chunks)
            except StopIteration:
                raise StopIteration(f'End of the dataset is reached: '
                                    f'dataset shape: {self.dataset.shape}, '
                                    f'requested index: {self.offset + n_items}.')
            self.data = np.concatenate((self.data, self.dataset[chunk_slice]), axis=0)

        start_idx = self.cursor
        self.cursor += n_items
        return self.data[start_idx: self.cursor]

    def __iter__(self):
        return self

    def __next__(self):
        return self.get_next(n_items=1)[0]

    def __len__(self):
        return self.dataset.shape[0]

    def __repr__(self):
        return (
            f'DatasetIterator: '
            f'path={self.dataset_path}, '
            f'shape={self.dataset.shape} '
            f'cursor={self.offset + self.cursor}'
        )


class HDF5Container:

    def __init__(self, container_path, mode='a', exclusive=False):

        # initializations
        self.container_path = pathlib.Path(container_path).expanduser()
        self.lock_handle = fasteners.InterProcessLock(f'{self.container_path}.lock')  # using temp folder wont work: in a cluster, the temp folder could be different for each node
        self.exclusive = exclusive
        self.dataset_defaults = dict(
            maxshape=(None,),
            chunks=(configurations.configs['concatemers']['hdf5_chunk_size'],),
            compression="gzip",
            compression_opts=configurations.configs['concatemers']['compression_level'],
            # track_order=True, # could cause problems if true, an HDF5 bug
        )

        # opening the file handle
        if self.exclusive:
            self.lock()
        logger.debug(f'Opening (mode={mode}): {self.container_path}')
        self.h5_file = h5py.File(self.container_path, mode=mode)

    def lock(self):
        logger.debug(f'Requesting (an exclusive) right to edit: {self.container_path}')
        self.lock_handle.acquire()
        logger.debug(f'Permission acquired: {self.container_path}')

    def unlock(self):
        self.lock_handle.release()
        lock_path = self.lock_handle.path.decode()
        # pathlib.Path(lock_path).unlink()
        logger.debug(f'Container lock is released: {lock_path}')

    def store(self, dataset_path, row_indices, values, exclusive=True):
        if exclusive:
            self.lock()
        assert dataset_path in self.h5_file, f'Dataset not found: {dataset_path}'
        assert not hasattr(values, '__iter__') or len(row_indices) == len(values)

        # reshape if needed
        max_index = np.max(row_indices)
        if max_index >= self.h5_file[dataset_path].shape[0]:
            logger.warning(f'Dataset size is smaller than input index. Increasing size of {dataset_path} '
                           f'from {self.h5_file[dataset_path].shape[0]} to {max_index}')
            self.h5_file[dataset_path].resize(max_index + 1, axis=0)

        # store
        self.h5_file[dataset_path][row_indices] = values
        if exclusive:
            self.unlock()

    def retrieve(self, dataset_path, row_indices, exclusive=True):
        if exclusive:
            self.lock()
        assert dataset_path in self.h5_file, f'Dataset not found: {dataset_path}'

        # check if out-of-bound indices exist
        max_index = np.max(row_indices)
        n_row = self.h5_file[dataset_path].shape[0]
        if max_index >= n_row:
            logger.warning(f'{dataset_path} (#row={n_row:,d}): Out-of-bound indices (maximum_index={max_index:,d}). These indices will be ignored.')
            row_indices = row_indices[row_indices < n_row]

        # retrieve
        values = self.h5_file[dataset_path][row_indices]
        if exclusive:
            self.unlock()
        return values

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        logger.debug(f'Closing (mode={self.h5_file.mode}): {self.h5_file.filename}')
        self.h5_file.close()
        if self.exclusive:
            self.unlock()
