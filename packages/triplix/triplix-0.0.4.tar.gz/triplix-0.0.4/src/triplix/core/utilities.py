
import os
# import time
import datetime
import random
import string
import socket
from typing import Dict

import numpy as np

from triplix._logging import get_logger

COMMAND_NAME = 'triplix.utilities'
logger = get_logger(COMMAND_NAME)


def get_random_string(length):
    # string.ascii_lowercase, string.ascii_letters, string.punctuation
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


def generate_prog_id():
    host_name = socket.gethostname()
    pid = os.getpid()
    str_time = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
    prog_id = f'{host_name}|{pid}|{str_time}'
    # get_random_string(configurations.configs['program_id_length'])
    return prog_id


def overlap(
        query_start, query_end,
        ref_start, ref_end,
        query_chrom=None, ref_chrom=None,
        ref_left_included=True,
        ref_right_included=True,
        offset=0
):

    # sanity checks
    if not isinstance(query_start, np.ndarray):
        query_start = np.array(query_start)
    if not isinstance(query_end, np.ndarray):
        query_end = np.array(query_end)
    if not isinstance(ref_start, np.ndarray):
        ref_start = np.array(ref_start)
    if not isinstance(ref_end, np.ndarray):
        ref_end = np.array(ref_end)
    assert query_start.ndim == 0 and query_end.ndim == 0, 'Query must be only one coordinate.'
    assert ref_start.ndim == 1 and ref_end.ndim == 1, 'Reference coordinates must expressed in a single column.'
    assert len(ref_start) == len(ref_end), 'Size inconsistency in reference coordinates: [start, end]'

    # check chromosome overlap, if needed
    if query_chrom is not None:
        if not isinstance(ref_chrom, np.ndarray):
            ref_chrom = np.array(ref_chrom)
        assert len(ref_start) == len(ref_chrom), 'Size inconsistency in reference coordinates: [chrom, start]'
        is_cis = query_chrom == ref_chrom
    else:
        is_cis = np.ones(len(ref_start), dtype=bool)

    # check coordinate overlaps
    if ref_left_included:
        ovl_left = query_end >= ref_start - offset
    else:
        ovl_left = query_end > ref_start - offset
    if ref_right_included:
        ovl_right = query_start <= ref_end + offset
    else:
        ovl_right = query_start < ref_end + offset

    return is_cis & ovl_left & ovl_right


def triplet_to_cube(
        triplets: Dict,
        anchor_edges: np.ndarray,
        anchor_width=None,
        data_cols=('count_ABC',),
        start_cols=('start_A', 'start_B', 'start_C'),
        end_cols=('end_A', 'end_B', 'end_C'),
        unique_col='read_id',
        symmetric=True,
):
    def update_cube_if_unique():
        voxel_id = (idx_a, idx_b, idx_c)
        if voxel_id not in seen_read_ids:
            seen_read_ids[voxel_id] = set()

        triplet_id = triplets[unique_col][trp_idx]
        if triplet_id in seen_read_ids[voxel_id]:
            return
        seen_read_ids[voxel_id].add(triplet_id)
        update_cube()

    def update_cube():
        if not (0 <= idx_a < n_anchor and 0 <= idx_b < n_anchor and 0 <= idx_c < n_anchor):
            return

        for col_name in data_cols:
            if np.isnan(cubes[col_name][idx_a, idx_b, idx_c]):
                data = triplets[col_name][trp_idx]
            else:
                data = triplets[col_name][trp_idx] + cubes[col_name][idx_a, idx_b, idx_c]

            cubes[col_name][idx_a, idx_b, idx_c] = data
            if symmetric:
                cubes[col_name][idx_a, idx_c, idx_b] = data
                cubes[col_name][idx_b, idx_a, idx_c] = data
                cubes[col_name][idx_b, idx_c, idx_a] = data
                cubes[col_name][idx_c, idx_a, idx_b] = data
                cubes[col_name][idx_c, idx_b, idx_a] = data

    if unique_col is None:
        update_func = update_cube
    else:
        seen_read_ids = {}
        update_func = update_cube_if_unique

    # find overlapping anchors
    overlap_intervals = []
    for start_cname, end_cname in zip(start_cols, end_cols):
        anchor_starts = triplets[start_cname]
        if anchor_width is None:
            anchor_ends = triplets[end_cname]
        else:
            anchor_ends = triplets[start_cname] + anchor_width
        overlap_intervals.append(np.searchsorted(anchor_edges, [anchor_starts, anchor_ends - 1], side='right') - 1)

    # check for uniqueness of bin_idxs, if needed
    if unique_col is None:
        indices_all = np.vstack(overlap_intervals).T
        indices_unq = np.unique(indices_all, axis=0)
        assert len(indices_unq) == len(indices_unq), 'Non-unique indices are found'
        del indices_all, indices_unq

    # prepare the cube
    n_anchor = len(anchor_edges) - 1
    cubes = {col: np.full([n_anchor, n_anchor, n_anchor], fill_value=np.nan) for col in data_cols}

    # fill up the cubes
    n_triplet = len(triplets[start_cols[0]])
    single_overlaps = (
            (overlap_intervals[0][0] == overlap_intervals[0][1]) &
            (overlap_intervals[1][0] == overlap_intervals[1][1]) &
            (overlap_intervals[2][0] == overlap_intervals[2][1])
    )
    for trp_idx in range(n_triplet):
        if single_overlaps[trp_idx]:
            idx_a, idx_b, idx_c = overlap_intervals[0][0][trp_idx], overlap_intervals[1][0][trp_idx], overlap_intervals[2][0][trp_idx]
            update_func()
        else:
            range_a = range(overlap_intervals[0][0][trp_idx], overlap_intervals[0][1][trp_idx] + 1)
            range_b = range(overlap_intervals[1][0][trp_idx], overlap_intervals[1][1][trp_idx] + 1)
            range_c = range(overlap_intervals[2][0][trp_idx], overlap_intervals[2][1][trp_idx] + 1)
            for idx_a in range_a:
                for idx_b in range_b:
                    for idx_c in range_c:
                        update_func()

    return cubes


def merge_intervals(intervals, chroms_order=None, check_coverage=False, verbose=False):

    # sort intervals
    if chroms_order is not None:
        chrom2idx = {chrom: idx for idx, chrom in enumerate(chroms_order)}
        intervals = sorted(intervals, key=lambda chk: (chrom2idx[chk[0]], chk[1], chk[2]))
    n_intrv = len(intervals)
    assert n_intrv > 0

    merged = [intervals[0]]
    for idx in range(1, n_intrv):
        interval = intervals[idx]

        if merged[-1][0] != interval[0]:
            merged.append(interval)
        elif merged[-1] == interval:
            if verbose:
                logger.warning(f'Identical intervals: Ignoring "{interval}"')
        elif merged[-1][2] == interval[1]:
            merged[-1][2] = interval[2]
        elif merged[-1][2] > interval[1] and merged[-1][1] < interval[2]:
            if check_coverage:
                raise ValueError(f'Overlapping intervals are found: A={merged[-1]} and B={interval}')
            merged.append(interval)
        else:
            message = f'An uncovered area is found between "{merged[-1]}" and "{interval}"'
            if check_coverage:
                raise ValueError(message)
            merged.append(interval)

    return merged

