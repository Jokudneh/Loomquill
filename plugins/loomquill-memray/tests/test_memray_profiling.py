from unittest.mock import Mock, patch
import pytest
from flytekit import task, current_context
from flytekitplugins.memray import memray_profiling


@task(enable_deck=True)
@memray_profiling
def heavy_compute(i: int) -> int:
    return i + 1


def test_local_exec():
    heavy_compute(i=7)
    assert (
