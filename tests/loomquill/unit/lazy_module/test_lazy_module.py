import sys
from unittest.mock import Mock

import pytest
from flytekit.lazy_import.lazy_module import _LazyModule, lazy_module, is_imported


def test_lazy_module():
