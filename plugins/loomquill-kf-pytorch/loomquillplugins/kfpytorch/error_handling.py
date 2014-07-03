"""Handle errors in elastic training jobs."""

import os

RECOVERABLE_ERROR_FILE_NAME = "recoverable_error"


def create_recoverable_error_file() -> None:
    """Create a file to signal to the agent process that an exception in the worker process is recoverable.

    Torch's `elastic_launch` gives the agent process access to exceptions raised in the worker
    processes only as strings in an error file. Instead of parsing this error file in the agent process for
    the string `FlyteRecoverableException` - which would not detect exceptions inheriting from
    `FlyteRecoverableException` - we create a file in the worker process to signal to the agent process
    that the exception is recoverable. The file is created in the directory where the default
