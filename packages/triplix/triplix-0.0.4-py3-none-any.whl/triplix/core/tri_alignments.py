import gzip
import pathlib
# from itertools import compress
import re
from typing import Union, Optional, Iterable
# from collections import deque

import numpy as np
import pandas as pd
import pypairix
from triplix.core.header import TriplixHeader
# from triplix.core import configurations
# from triplix.core.utilities import overlap
from triplix._logging import get_logger

COMMAND_NAME = 'triplix.tri-alignments'
logger = get_logger(COMMAND_NAME)


class TriAlignments(dict):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.options = {
            'display.min_rows': 5
        }
        self.columns_dtypes = {
            'start_A': int, 'start_B': int, 'start_C': int,
            'end_A': int, 'end_B': int, 'end_C': int,
            'mapq_A': int, 'mapq_B': int, 'mapq_C': int,
        }
        # self.columns_integer = {col for col in self.return_columns if tri_container.columns_dtypes.get(col, None) is int}

        self.initialize()

    def initialize(self):
        for anc_lbl in ['A', 'B', 'C']:
            for anc_type in ['chrom', 'start', 'end']:
                self[f'{anc_type}_{anc_lbl}'] = []

    def __repr__(self):
        if 'start_A' not in self:
            return '<Miss-formatted Tri-alignments>: Missing `start_A` column'

        n_row = len(self['start_A'])
        n_show = self.options['display.min_rows']
        if n_row == 0 or n_row <= n_show:
            show_df = pd.DataFrame(self).astype(str)
        else:
            show_idxs = list(range(0, n_show + 1)) + list(range(n_row - n_show, n_row))
            show_df = pd.DataFrame({key: np.array(values)[show_idxs] for (key, values) in self.items()}, index=show_idxs)
            show_df = show_df.astype(str)
            show_df.loc[n_show, :] = '***'
            show_df.index = show_df.index.astype(str)
            show_df.rename({str(n_show): '***'}, axis=0, inplace=True)
        return '<Tri-alignments>:\n' + repr(show_df)

    def __len__(self):
        for column in self.keys():
            return len(self[column])

    def convert_dtypes(self):
        for hdr in self.keys():
            known_dtype = self.columns_dtypes.get(hdr, None)
            if known_dtype is int:
                self[hdr] = np.array(self[hdr], dtype=int)
            else:
                self[hdr] = np.array(self[hdr], dtype=object)

    def to_dataframe(self, *args, **kwargs):
        return pd.DataFrame(self, *args, **kwargs)


class TriAlignmentsContainer:

    def __init__(self, trialn_path: Union[str, pathlib.Path]):
        self.trialn_path = pathlib.Path(trialn_path).expanduser()
        self.header = TriplixHeader(file_path=trialn_path)
        self.column_names = self.header.column_names
        self.col2idx = {col: idx for idx, col in enumerate(self.column_names)}

        # initialize PyPairix object, if possible
        try:
            self.px_obj = pypairix.open(str(self.trialn_path))
            logger.debug(f'Loaded Pairix index of: {self.trialn_path}')
        except pypairix.PairixError:
            self.px_obj = None
            logger.warning(f'Failed to load Pairix index: {self.trialn_path}')

    def fetch(
            self,
            chrom_a: Optional[str] = None, start_a: Optional[float] = None, end_a: Optional[float] = None,
            chrom_b: Optional[str] = None, start_b: Optional[float] = None, end_b: Optional[float] = None,
            chrom_c: Optional[str] = None, start_c: Optional[float] = None, end_c: Optional[float] = None,
            batch_size=int(1e6), filter_c=True,
            mapping_quality: Optional[int] = None,
            return_columns: Optional[Iterable] = None,
            read_regex: str = None,
            experiment_regex: str = None,
    ):

        # set the default values
        if chrom_a is None:
            return self.gzip_iter(mapping_quality)
        else:
            if self.px_obj is None:
                index_filepath = self.trialn_path.parent / (self.trialn_path.name + '.px2')
                if not index_filepath.is_file():
                    raise FileNotFoundError(
                        f'Tri-alignment\'s index file ({index_filepath}) is not found. '
                        f'Please index the Tri-alignments file first using `triplix index` command.'
                    )
                raise pypairix.PairixError(f'Failed to load Tri-alignment\'s index file ({index_filepath}). ')

            if chrom_b is None:
                chrom_b = chrom_a
            if chrom_c is None:
                chrom_c = chrom_b
            if start_b is None:
                start_b = start_a
            if start_c is None:
                start_c = start_b
            if end_b is None:
                end_b = end_a
            if end_c is None:
                end_c = end_b
            assert isinstance(chrom_a, str) and len(chrom_a) > 0
            assert isinstance(chrom_b, str) and len(chrom_b) > 0
            assert isinstance(chrom_c, str) and len(chrom_c) > 0
            # assert np.isfinite(start_A)
            # assert np.isfinite(start_B)
            # assert np.isfinite(start_C)
            # assert np.isfinite(end_A)
            # assert np.isfinite(end_B)
            # assert np.isfinite(end_C)

            return TriAlignmentIterator(
                self,
                chrom_a=chrom_a, start_a=int(start_a), end_a=int(end_a),
                chrom_b=chrom_b, start_b=int(start_b), end_b=int(end_b),
                chrom_c=chrom_c, start_c=int(start_c), end_c=int(end_c),
                batch_size=batch_size, filter_c=filter_c, return_columns=return_columns,
                mapping_quality=mapping_quality,
                read_regex=read_regex,
                experiment_regex=experiment_regex,
            )

    def fetch_slice(
            self,
            vp_chrom, vp_start, vp_end,
            anchor_edges,
            anchor_max_distance=int(2e6),
            mapping_quality=5,

    ):
        n_anchor = len(anchor_edges) - 1
        counts = np.zeros([n_anchor, n_anchor], dtype=int)
        for aj in range(n_anchor):
            if anchor_edges[aj] < vp_start:
                continue
            if anchor_edges[aj] - vp_start > anchor_max_distance:
                break

            tri_alignments_iter = self.fetch(
                chrom_a=vp_chrom, start_a=vp_start, end_a=vp_end,
                chrom_b=vp_chrom, start_b=anchor_edges[aj], end_b=anchor_edges[aj + 1] - 1,
                chrom_c=vp_chrom, start_c=anchor_edges[aj], end_c=anchor_edges[-1] - 1,
                batch_size=int(1e6), mapping_quality=mapping_quality, return_columns=[
                    'read_name',
                    'chrom_C', 'start_C', 'end_C',
                    'mapq_A', 'mapq_B', 'mapq_C',
                ],
            )
            for tri_alignments in tri_alignments_iter:
                # tri_alignments.to_dataframe()

                # filter alignments with low mapping quality
                # is_mapped = (
                #         (tri_alignments['mapq_A'] >= mapping_quality) &
                #         (tri_alignments['mapq_B'] >= mapping_quality) &
                #         (tri_alignments['mapq_C'] >= mapping_quality)
                #
                # )
                # if not np.all(is_mapped):
                #     for hdr in tri_alignments.keys():
                #         tri_alignments[hdr] = tri_alignments[hdr][is_mapped]

                # find overlaps across bins
                start_idxs = np.searchsorted(anchor_edges, tri_alignments['start_C'], side='right') - 1
                end_idxs = np.searchsorted(anchor_edges, tri_alignments['end_C'], side='right') - 1

                # make sure each read contributes only once to each Triplet
                seen_ids = [set() for _ in range(n_anchor)]
                for start_idx, end_idx, read_id in zip(start_idxs, end_idxs, tri_alignments['read_name']):
                    for ak in range(start_idx, end_idx + 1):
                        if anchor_edges[ak] - vp_start > anchor_max_distance:
                            continue
                        if not aj <= ak < n_anchor:  # n_bin is needed, as the `alignment_end` could still fall outside `load_end`
                            continue
                        if read_id in seen_ids[ak]:
                            continue

                        seen_ids[ak].add(read_id)
                        counts[aj, ak] += 1
        return counts

    def gzip_iter(self, mapping_quality=None):
        with gzip.open(self.trialn_path, 'rt') as gz_file:

            # skipping the header lines
            for line in gz_file:
                if line.startswith('#column names:'):
                    break

            # iterate over the rest of the lines, returning a list of columns
            if mapping_quality is None:
                for line in gz_file:
                    yield line.rstrip().split('\t')
            else:
                for line in gz_file:
                    # filter for mapping quality
                    if (
                            int(line[self.col2idx['mapq_A']]) < mapping_quality
                            or int(line[self.col2idx['mapq_B']]) < mapping_quality
                            or int(line[self.col2idx['mapq_C']]) < mapping_quality
                    ):
                        continue
                    yield line.rstrip().split('\t')


class TriAlignmentIterator:
    """
    Collect Tri-alignments overlapping with a given a given tri-coordinates
    :param chrom_a: chromosome A of the Tri-alignments of interest
    :param chrom_b: chromosome B of the Tri-alignments of interest
    :param chrom_c: chromosome C of the Tri-alignments of interest
    :param start_a: start position of the A interval
    :param start_b: start position of the B interval
    :param start_c: start position of the C interval
    :param end_a: end position of the A interval
    :param end_b: end position of the B interval
    :param end_c: end position of the C interval
    :param batch_size: number of Tri-alignments to load in each iteration
    :param filter_c: whether the Tri-alignments should be filtered to have overlap with *_C interval
    :param mapping_quality: the minimum mapping quality that the alignments (of a tri-alignment) should have to be considered valid.

    Note:
        [start|end]_[A|B|C] : coordinates are inclusive on both sides
    """

    def __init__(
            self, tri_container: TriAlignmentsContainer,
            chrom_a: str, start_a: int, end_a: int,
            chrom_b: str, start_b: int, end_b: int,
            chrom_c: str, start_c: int, end_c: int,
            batch_size: int,
            filter_c=True, return_columns=None,
            mapping_quality=None,
            read_regex=None,
            experiment_regex=None,
    ):
        self.chrom_c = chrom_c
        self.start_c = start_c
        self.end_c = end_c
        self.batch_size = batch_size
        self.filter_C = filter_c
        self.mapping_quality = mapping_quality
        if read_regex is None:
            self.read_regex = None
        else:
            self.read_regex = re.compile(self.read_regex)
        if experiment_regex is None:
            self.experiment_regex = None
        else:
            self.experiment_regex = re.compile(experiment_regex)
        self.col2idx = tri_container.col2idx
        if return_columns is None:
            self.return_columns = tri_container.column_names
        else:
            self.return_columns = return_columns
        self.EOF = False

        if self.filter_C:
            headers_c = ['chrom_C', 'start_C', 'end_C']
            assert all(hdr in self.return_columns for hdr in headers_c), f'The following columns must be included in the `return_columns`: {headers_c}'

        # initialize query2D object
        self.trialn_iter = tri_container.px_obj.query2D(chrom_a, start_a, end_a,
                                                        chrom_b, start_b, end_b)

    def __iter__(self):
        return self

    def __next__(self):
        if self.EOF:
            raise StopIteration()

        # initialize a Tri-alignments container
        tri_alignments = TriAlignments()
        for col in self.return_columns:
            tri_alignments[col] = []

        # load a batch of tri-alignments
        n_load = 0
        for line in self.trialn_iter:

            # tri-alignment filters
            if self.mapping_quality is not None:
                is_mapped = (
                        int(line[self.col2idx['mapq_A']]) >= self.mapping_quality and
                        int(line[self.col2idx['mapq_B']]) >= self.mapping_quality and
                        int(line[self.col2idx['mapq_C']]) >= self.mapping_quality
                )
                if not is_mapped:
                    continue
            if self.read_regex is not None:
                read_name = line[self.col2idx['read_name']]
                if not self.read_regex.match(read_name):
                    continue
            if self.experiment_regex is not None:
                experiment_name = line[self.col2idx['experiment_name']]
                if not self.experiment_regex.match(experiment_name):
                    continue

            # adding the tri-alignment
            for hdr in tri_alignments.keys():
                tri_alignments[hdr].append(line[self.col2idx[hdr]])
            n_load += 1
            if n_load >= self.batch_size:
                break
        else:
            self.EOF = True

        # convert the columns dtypes
        tri_alignments.convert_dtypes()

        if n_load == 0:
            raise StopIteration()

        # filter rows, if needed
        if self.filter_C:
            has_ovl = (
                    (self.chrom_c == tri_alignments['chrom_C'])
                    & (self.start_c <= tri_alignments['end_C'])
                    & (self.end_c >= tri_alignments['start_C'])
            )
            if not np.all(has_ovl):
                for hdr in tri_alignments.keys():
                    tri_alignments[hdr] = tri_alignments[hdr][has_ovl]

        return tri_alignments
