from click.testing import CliRunner
from unittest.mock import patch

from flytekit.clis.sdk_in_container.serve import serve


def test_agent_prometheus_port():
    runner = CliRunner()
    test_port = 9100
    test_prometheus_port = 9200
    test_worker = 5
    test_timeout = 30

    with patch('flytekit.clis.sdk_in_container.serve._start_grpc_server') as mock_start_grpc:
        result = runner.invoke(
            serve,
            [
                'agent',
                '--port', str(test_port),
                '--prometheus_port', str(test_prometheus_port),
