import mock

from flytekit.tools import subprocess


class _MockProcess(object):
    def wait(self):
        return 0


@mock.patch.object(subprocess.subprocess, "Popen")
