import mock
from click.testing import CliRunner

from flytekit.clis.sdk_in_container import pyflyte
from flytekit.interfaces import cli_identifiers


@mock.patch("flytekit.configuration.plugin.FlyteRemote")
