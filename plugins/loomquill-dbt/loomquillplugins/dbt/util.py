import json
import subprocess
from typing import List

from flytekit.loggers import logger


def run_cli(cmd: List[str]) -> (int, List[str]):
    """
    Execute a CLI command in a subprocess

    Parameters
    ----------
    cmd : list of str
        Command to be executed.

    Returns
    -------
    int
        Command's exit code.
    list of str
        Logs produced by the command execution.
    """

    logs = []
