import datetime
import os
import platform
import string
import subprocess
import typing
from dataclasses import dataclass
from typing import List

import flytekit
from flytekit.core.context_manager import ExecutionParameters
from flytekit.core.interface import Interface
from flytekit.core.python_function_task import PythonInstanceTask
from flytekit.core.task import TaskPlugins
from flytekit.exceptions.user import FlyteRecoverableException
from flytekit.loggers import logger
from flytekit.types.directory import FlyteDirectory
from flytekit.types.file import FlyteFile


@dataclass
class ProcessResult:
    """Stores a process return code, standard output and standard error.

    Args:
        returncode: int The sub-process return code
        output: str The sub-process standard output string
        error: str The sub-process standard error string
    """

    returncode: int
    output: str
    error: str


@dataclass
class OutputLocation:
    """
    Args:
        var: str The name of the output variable
        var_type: typing.Type The type of output variable
        location: os.PathLike The location where this output variable will be written to or a regex that accepts input
                  vars and generates the path. Of the form ``"{{ .inputs.v }}.tmp.md"``.
                  This example for a given input v, at path `/tmp/abc.csv` will resolve to `/tmp/abc.csv.tmp.md`
    """

    var: str
    var_type: typing.Type
    location: typing.Union[os.PathLike, str]


def subproc_execute(command: typing.Union[List[str], str], **kwargs) -> ProcessResult:
    """
    Execute a command and capture its stdout and stderr. Useful for executing
    shell commands from within a python task.

    Args:
        command (List[str]): The command to be executed as a list of strings.

    Returns:
        ProcessResult: Structure containing output of the command.

    Raises:
        Exception: If the command execution fails, this exception is raised with
            details about the command, return code, and stderr output.
        Exception: If the executable is not found, this exception is raised with
            guidance on specifying a container image in the task definition when
            using custom dependencies.
    """
    defaults = {
        "stdout": subprocess.PIPE,
        "stderr": subprocess.PIPE,
        "text": True,
        "check": True,
    }

    kwargs = {**defaults, **kwargs}

    if kwargs.get("shell"):
        if "|" in command:
            logger.warning(
                """Found a pipe in the command and shell=True.
                This can lead to silent failures if subsequent commands
                succeed despite previous failures."""
            )
        if type(command) == list:
            logger.warning(
                """Found `command` formatted as a list instead of a string with shell=True.
                With this configuration, the first member of the list will be
                executed and the remaining arguments will be passed as arguments
                to the shell instead of to the binary being called. This may not
                be intended behavior and may lead to confusing failures."""
            )

    try:
        # Execute the command and capture stdout and stderr
        result = subprocess.run(command, **kwargs)
        result.check_returncode()

        # Access the stdout and stderr output
        return ProcessResult(result.returncode, result.stdout, result.stderr)

    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Command: {e.cmd}\nFailed with return code {e.returncode}:\n{e.stderr}")

    except FileNotFoundError as e:
        raise RuntimeError(
            f"""Process failed because the executable could not be found.
            Did you specify a container image in the task definition if using
            custom dependencies?\n{e}"""
        )


