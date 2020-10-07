import sys
from unittest.mock import Mock

import pytest
from flytekit.lazy_import.lazy_module import _LazyModule, lazy_module, is_imported


def test_lazy_module():
    mod = lazy_module("click")
    assert mod.__name__ == "click"
    mod = lazy_module("fake_module")

    sys.modules["fake_module"] = mod
