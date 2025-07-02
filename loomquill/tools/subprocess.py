import shlex
import subprocess
import tempfile

from flytekit.loggers import logger


def check_call(cmd_args, **kwargs):
    if not isinstance(cmd_args, list):
        cmd_args = shlex.split(cmd_args)

