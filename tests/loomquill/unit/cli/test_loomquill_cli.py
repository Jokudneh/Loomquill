import mock
import pytest
from click.testing import CliRunner as _CliRunner

from flytekit.clis.flyte_cli import main as _main
from flytekit.exceptions.user import FlyteAssertion
from flytekit.models import filters as _filters
from flytekit.models.admin import common as _admin_common
from flytekit.models.core import identifier as _core_identifier
from flytekit.models.project import Project as _Project

mm = mock.MagicMock()
mm.return_value = 100


@mock.patch("flytekit.clis.flyte_cli.main.utils")
def test__extract_files_with_unspecified_resource_type(load_mock):
    id = _core_identifier.Identifier(
        _core_identifier.ResourceType.UNSPECIFIED,
        "myproject",
