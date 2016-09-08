import os
import sys

import mock
import pytest
from click.testing import CliRunner

from flytekit import configuration as _config
from flytekit.clis.sdk_in_container import constants as _constants
from flytekit.clis.sdk_in_container import pyflyte as _pyflyte
from flytekit.tools import module_loader as _module_loader


def _fake_module_load(names):
    assert names == ("common.workflows",)
    from common.workflows import simple

    yield simple

