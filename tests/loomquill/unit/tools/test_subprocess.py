import mock

from flytekit.tools import subprocess


class _MockProcess(object):
    def wait(self):
        return 0


@mock.patch.object(subprocess.subprocess, "Popen")
def test_check_call(mock_call):
    mock_call.return_value = _MockProcess()
