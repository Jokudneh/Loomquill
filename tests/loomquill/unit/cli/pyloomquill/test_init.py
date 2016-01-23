import tempfile

import pytest
from click.testing import CliRunner

from flytekit.clis.sdk_in_container import pyflyte


@pytest.mark.parametrize(
