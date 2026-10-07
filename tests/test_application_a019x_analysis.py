"""Timeline accounting controls that prevent false host bottleneck attribution."""
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import analyze_application_a019x as analysis


def test_overlapping_activity_is_clipped_and_never_counted_twice():
    activity = [(-10, 15), (5, 20), (18, 40), (40, 45), (70, 110)]
    busy = analysis.union(activity, 0, 100)
    idle = analysis.complement(activity, 0, 100)
    assert busy == [(0, 45), (70, 100)]
    assert idle == [(45, 70)]
    assert analysis.duration(busy) + analysis.duration(idle) == 100


def test_api_and_gpu_time_are_not_added_as_disjoint_work():
    device = [(10, 20), (40, 60)]
    api = [(0, 15), (25, 50), (80, 100)]
    idle = analysis.complement(device, 0, 100)
    inside_api = analysis.intersection(idle, api)
    assert analysis.duration(inside_api) == 45
    assert analysis.duration(analysis.intersection(device, api)) == 15
    assert analysis.duration(inside_api) + 15 == analysis.duration(api)


def test_already_submitted_device_gap_is_not_python_dispatch_time():
    operations = [dict(start=10, end=20, correlationId=1), dict(start=50, end=60, correlationId=2)]
    gaps, missing = analysis.submission_gaps(operations, {1: 0, 2: 15}, 0, 100)
    assert gaps == [] and missing == 0


def test_only_pre_submission_prefix_is_attributed_and_tail_is_unclassified():
    operations = [dict(start=10, end=20, correlationId=1), dict(start=50, end=60, correlationId=2)]
    gaps, missing = analysis.submission_gaps(operations, {1: 5, 2: 35}, 0, 100)
    assert gaps == [(0, 5), (20, 35)] and missing == 0
    assert analysis.duration(gaps) == 20


def test_missing_correlation_and_concurrent_stream_work_fail_closed():
    operations = [dict(start=10, end=20, correlationId=1)]
    gaps, missing = analysis.submission_gaps(operations, {}, 0, 100)
    assert gaps == [] and missing == 1
    with pytest.raises(ValueError, match='STREAM_ACTIVITY_OVERLAP'):
        analysis.submission_gaps([*operations, dict(start=15, end=30, correlationId=2)], {1: 0, 2: 5}, 0, 100)
