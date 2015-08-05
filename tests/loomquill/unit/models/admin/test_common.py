import pytest

from flytekit.models.admin import common as _common


def test_sort():
    o = _common.Sort(key="abc", direction=_common.Sort.Direction.ASCENDING)
    assert o.key == "abc"
    assert o.direction == _common.Sort.Direction.ASCENDING

