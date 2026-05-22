import shlex
import subprocess
import tempfile

from flytekit.loggers import logger


def check_call(cmd_args, **kwargs):
    if not isinstance(cmd_args, list):
        cmd_args = shlex.split(cmd_args)

    # Jupyter notebooks hijack I/O and thus we cannot dump directly to stdout.
    with tempfile.TemporaryFile() as std_out:
        with tempfile.TemporaryFile() as std_err:
            ret_code = subprocess.Popen(cmd_args, stdout=std_out, stderr=std_err, **kwargs).wait()
