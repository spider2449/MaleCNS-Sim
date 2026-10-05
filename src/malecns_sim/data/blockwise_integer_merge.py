"""A018T bounded NumPy merge; experimental opt-in only."""
from functools import partial
import sys
import time
import numpy as np
from .integer_aggregation import experimental_load_aggregated_publication_numeric
from .single_pass_integer_merge import compact_output


def key_less(a_pre, a_post, b_pre, b_post):
    """Exact int64 lexicographic comparison, also supporting numeric arrays."""
    return (a_pre < b_pre) | ((a_pre == b_pre) & (a_post < b_post))


def upper_bound(run, start, end, pre, post):
    """Find the first key strictly above a two-key boundary in a bounded view."""
    first = int(np.searchsorted(run[0][start:end], pre, side="left")) + start
    last = int(np.searchsorted(run[0][first:end], pre, side="right")) + first
    return first + int(np.searchsorted(run[1][first:last], post, side="right"))


def merge_sorted_runs(left, right, *, block_size=16384, metrics=None):
    """Merge sorted internally unique nonnegative int64 runs in closed blocks.

    Each side contributes at most floor(block_size/2) rows. The smaller of
    the two slice endpoints closes the block, including equality on both sides.
    Internal uniqueness limits every grouped key to two contributions.
    """
    if block_size < 2:
        raise ValueError("block_size must be at least two")
    n, m = left[0].size, right[0].size
    output = tuple(np.empty(n+m, dtype=np.int64) for _ in range(3))
    i = j = used = 0
    half = block_size // 2
    limit = np.int64(np.iinfo(np.int64).max)
    while i < n and j < m:
        end_i, end_j = min(i+half, n), min(j+half, m)
        if key_less(left[0][end_i-1], left[1][end_i-1],
                    right[0][end_j-1], right[1][end_j-1]):
            pre, post = left[0][end_i-1], left[1][end_i-1]
        else:
            pre, post = right[0][end_j-1], right[1][end_j-1]
        next_i = upper_bound(left, i, end_i, pre, post)
        next_j = upper_bound(right, j, end_j, pre, post)
        columns = tuple(np.concatenate((a[i:next_i], b[j:next_j]))
                        for a, b in zip(left, right))
        order = np.lexsort((columns[1], columns[0]))
        keys_pre, keys_post, values = (a[order] for a in columns)
        equal = ((keys_pre[1:] == keys_pre[:-1]) &
                 (keys_post[1:] == keys_post[:-1]))
        duplicate = np.flatnonzero(equal)
        # Never perform a possibly overflowing addition. Counts are nonnegative.
        if np.any(values[duplicate] > limit - values[duplicate+1]):
            raise OverflowError("grouped synapse count exceeds int64")
        values[duplicate] += values[duplicate+1]
        keep = np.empty(values.size, dtype=np.bool_)
        keep[0] = True
        keep[1:] = ~equal
        emitted = values.size - duplicate.size
        for target, source in zip(output, (keys_pre, keys_post, values)):
            target[used:used+emitted] = source[keep]
        if metrics is not None:
            metrics['block_operations'] += 1
            metrics['search_operations'] += 6
            metrics['sort_operations'] += 1
            metrics['block_rows'] += values.size
            metrics['max_block_rows'] = max(metrics['max_block_rows'], values.size)
        used += emitted
        i, j = next_i, next_j
        del columns, order, keys_pre, keys_post, values, equal, duplicate, keep, source, target
    # Exhausted-side tails need only native slice copies, no per-row comparisons.
    for run, start, end in ((left, i, n), (right, j, m)):
        for offset in range(start, end, block_size):
            stop = min(offset+block_size, end)
            length = stop-offset
            for target, source in zip(output, run):
                target[used:used+length] = source[offset:stop]
            used += length
            if metrics is not None:
                metrics['block_operations'] += 1
                metrics['block_rows'] += length
                metrics['max_block_rows'] = max(metrics['max_block_rows'], length)
    return compact_output(output, used) if used < n+m else output


def merge_staged_integer_runs(runs, metrics=None, observer=None, *, block_size=16384):
    """Consume a mutable list in source order, releasing each completed pair.

    The caller must transfer ownership and retain no aliases. Observer runs
    after group input release and must retain only weak references. Historical
    arrays are never recorded in metrics. Fan-in is exactly two.
    """
    started = time.perf_counter()
    metrics = {} if metrics is None else metrics
    if block_size < 2:
        raise ValueError("block_size must be at least two")
    metrics.update(block_operations=0, search_operations=0, sort_operations=0,
                   block_rows=0, max_block_rows=0, block_workspace_bound_bytes=128*block_size)
    initial_rows = sum(run[0].size for run in runs)
    metrics.update(merge_stages=0, merge_groups_per_stage=[], rows_read=0,
                   rows_written=0, compaction_rows_read=0, compaction_rows_written=0,
                   first_scan_rows=0, second_scan_rows=0, max_active_input_runs=0,
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
            result = merge_sorted_runs(left, right, block_size=block_size, metrics=metrics)
            output_bytes = 24 * result[0].size
            metrics["schedule"].append((metrics["merge_stages"], offset, n, m))
            metrics["rows_read"] += n+m
            metrics["first_scan_rows"] += n+m
            if result[0].size < n+m:
                metrics["compaction_rows_read"] += result[0].size
                metrics["compaction_rows_written"] += result[0].size
            metrics["rows_written"] += result[0].size
            metrics["max_active_input_runs"] = 2
            metrics["max_group_input_bytes"] = max(metrics["max_group_input_bytes"], 24*(n+m))
            metrics["max_output_bytes"] = max(metrics["max_output_bytes"], output_bytes)
            metrics["max_resident_payload_bytes"] = max(metrics["max_resident_payload_bytes"], resident+completed+24*(n+m)+output_bytes)
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
    metrics["array_header_bytes"] = 12 * sys.getsizeof(np.empty(0, dtype=np.int64))
    metrics["container_header_allowance_bytes"] = 2048 * (len(metrics["schedule"]) + 2)
    metrics["resident_bound_bytes"] = 72 * initial_rows + 128 * block_size + 8192 + 2048 * (len(metrics["schedule"]) + 2)
    metrics["row_touches"] = (metrics["rows_read"] + metrics["rows_written"] +
                              metrics["compaction_rows_read"] + metrics["compaction_rows_written"])
    metrics["merge_seconds"] = time.perf_counter() - started
    metrics["final_grouped_bytes"] = sum(a.nbytes for a in result)
    return result


experimental_load_blockwise_publication_numeric = partial(
    experimental_load_aggregated_publication_numeric, merger=merge_staged_integer_runs)
