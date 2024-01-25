import pytest
from click.testing import CliRunner
from mock import mock

from flytekit.clis.sdk_in_container import pyflyte
from flytekit.remote import FlyteRemote


@mock.patch("flytekit.configuration.plugin.FlyteRemote", spec=FlyteRemote)
@pytest.mark.parametrize(
    ("action", "expected_state"),
    [
