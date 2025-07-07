import mock
from click.testing import CliRunner

from flytekit.clis.sdk_in_container import pyflyte
from flytekit.interfaces import cli_identifiers


@mock.patch("flytekit.configuration.plugin.FlyteRemote")
def test_execution_recover(remote):
    runner = CliRunner()
    id = cli_identifiers.WorkflowExecutionIdentifier(project="p1", domain="d1", name="test-execution-id")

