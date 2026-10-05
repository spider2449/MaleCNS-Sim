"""Opt-in A018 in-memory merge of certified A017 sorted integer runs."""
from functools import partial
import sys
import time

import numpy as np

from .integer_aggregation import experimental_load_aggregated_publication_numeric


def merge_sorted_runs(left, right):
    """Two passes, exact owned output, no row-sized temporary workspace.

    Inputs must satisfy the certified A017 contract. Payload peak is
    24 * (len(left) + len(right) + output_rows) bytes. Only a fixed number
    of scalar cursors/values is live; no per-edge container is retained.
    """
    limit = int(np.iinfo(np.int64).max)
    n, m = left[0].size, right[0].size
    output = None
    for write in (False, True):
        i = j = used = 0
        while i < n or j < m:
            comparison = -1 if j == m else 1 if i == n else (
                -1 if left[0][i] < right[0][j] or (
                    left[0][i] == right[0][j] and left[1][i] < right[1][j])
                else 1 if left[0][i] > right[0][j] or (
                    left[0][i] == right[0][j] and left[1][i] > right[1][j]) else 0)
            if comparison < 0:
                pre, post, count = left[0][i], left[1][i], left[2][i]
                i += 1
            elif comparison > 0:
                pre, post, count = right[0][j], right[1][j], right[2][j]
                j += 1
            else:
                pre, post = left[0][i], left[1][i]
                count = int(left[2][i]) + int(right[2][j])
                if count > limit:
                    raise OverflowError("grouped synapse count exceeds int64")
                i += 1
                j += 1
            if write:
                output[0][used], output[1][used], output[2][used] = pre, post, count
            used += 1
        if not write:
            output = tuple(np.empty(used, dtype=np.int64) for _ in range(3))
    return output


def merge_staged_integer_runs(runs, metrics=None, observer=None):
    """Consume a mutable list in source order, releasing each completed pair.

    The caller must transfer ownership and retain no aliases. Observer runs
    after group input release and must retain only weak references. Historical
    arrays are never recorded in metrics. Fan-in is exactly two.
    """
    started = time.perf_counter()
    metrics = {} if metrics is None else metrics
    initial_rows = sum(run[0].size for run in runs)
    metrics.update(merge_stages=0, merge_groups_per_stage=[], rows_read=0,
                   rows_written=0, max_active_input_runs=0,
                   max_group_input_bytes=0, max_output_bytes=0,
                   max_completed_next_stage_bytes=0, max_resident_payload_bytes=24*initial_rows,
                   initial_partial_bytes=24*initial_rows, schedule=[])
    current = runs
    while len(current) > 1:
        following = []
        completed = 0
        resident = sum(24 * run[0].size for run in current)
        groups = 0
        for offset in range(0, len(current), 2):
            left = current[offset]
            if offset + 1 == len(current):
                current[offset] = None
                following.append(left)
                completed += 24 * left[0].size
                resident -= 24 * left[0].size
                del left
                continue
            right = current[offset+1]
            n, m = left[0].size, right[0].size
            result = merge_sorted_runs(left, right)
            output_bytes = 24 * result[0].size
            metrics["schedule"].append((metrics["merge_stages"], offset, n, m))
            metrics["rows_read"] += 2 * (n+m)
            metrics["rows_written"] += result[0].size
            metrics["max_active_input_runs"] = 2
            metrics["max_group_input_bytes"] = max(metrics["max_group_input_bytes"], 24*(n+m))
            metrics["max_output_bytes"] = max(metrics["max_output_bytes"], output_bytes)
            metrics["max_resident_payload_bytes"] = max(metrics["max_resident_payload_bytes"], resident+completed+output_bytes)
            current[offset] = current[offset+1] = None
            del left, right
            resident -= 24*(n+m)
            following.append(result)
            completed += output_bytes
            del result
            groups += 1
            if observer is not None:
                observer(current, following)
        metrics["max_completed_next_stage_bytes"] = max(metrics["max_completed_next_stage_bytes"], completed)
        current.clear()
        current = following
        metrics["merge_stages"] += 1
        metrics["merge_groups_per_stage"].append(groups)
    result = current.pop() if current else tuple(np.empty(0, dtype=np.int64) for _ in range(3))
    # Container sizes are operational O(run count); scalar workspace is fixed.
    metrics["scalar_workspace_allowance_bytes"] = 4096
    metrics["array_header_bytes"] = 9 * sys.getsizeof(np.empty(0, dtype=np.int64))
    metrics["container_header_allowance_bytes"] = 2048 * (len(metrics["schedule"]) + 2)
    metrics["resident_bound_bytes"] = 48 * initial_rows + 8192 + 2048 * (len(metrics["schedule"]) + 2)
    metrics["merge_seconds"] = time.perf_counter() - started
    metrics["final_grouped_bytes"] = sum(a.nbytes for a in result)
    return result


experimental_load_staged_publication_numeric = partial(
    experimental_load_aggregated_publication_numeric, merger=merge_staged_integer_runs)
