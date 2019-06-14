import mock
import pytest
from typing_extensions import Annotated
import sys

from flytekit import StructuredDataset, kwtypes, task, workflow

try:
    import numpy as np
    numpy_installed = True
except ImportError:
    numpy_installed = False

skip_if_wrong_numpy_version = pytest.mark.skipif(
    not numpy_installed or np.__version__ > '1.26.4',
    reason="Test skipped because either NumPy is not installed or the installed version is greater than 1.26.4. "
           "Ensure that NumPy is installed and the version is <= 1.26.4, as required by the Snowflake connector."

)

@pytest.mark.skipif("pandas" not in sys.modules, reason="Pandas is not installed.")
@skip_if_wrong_numpy_version
@mock.patch("flytekit.types.structured.snowflake.get_private_key", return_value="pb")
@mock.patch("snowflake.connector.connect")
def test_sf_wf(mock_connect, mock_get_private_key):
    import pandas as pd
    from flytekit.lazy_import.lazy_module import is_imported
