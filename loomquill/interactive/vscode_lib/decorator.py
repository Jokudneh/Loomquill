import inspect
import json
import multiprocessing
import os
import platform
import shutil
import subprocess
import sys
import tarfile
import time
from typing import Callable, List, Optional

import fsspec

import flytekit
from flytekit.core.context_manager import FlyteContextManager
from flytekit.core.utils import ClassDecorator
from flytekit.interactive.constants import EXIT_CODE_SUCCESS, MAX_IDLE_SECONDS
from flytekit.interactive.utils import (
    execute_command,
    load_module_from_path,
)
from flytekit.interactive.vscode_lib.config import VscodeConfig
from flytekit.interactive.vscode_lib.vscode_constants import (
    DOWNLOAD_DIR,
    EXECUTABLE_NAME,
    HEARTBEAT_PATH,
    INTERACTIVE_DEBUGGING_FILE_NAME,
    RESUME_TASK_FILE_NAME,
    TASK_FUNCTION_SOURCE_PATH,
)


def exit_handler(
    child_process: multiprocessing.Process,
    task_function,
    args,
    kwargs,
    max_idle_seconds: int = 180,
    post_execute: Optional[Callable] = None,
):
    """
    1. Check the modified time of ~/.local/share/code-server/heartbeat.
       If it is older than max_idle_second seconds, kill the container.
       Otherwise, check again every HEARTBEAT_CHECK_SECONDS.
    2. Wait for user to resume the task. If resume_task is set, terminate the VSCode server, reload the task function, and run it with the input of the task.

    Args:
        child_process (multiprocessing.Process, optional): The process to be terminated.
        max_idle_seconds (int, optional): The duration in seconds to live after no activity detected.
        post_execute (function, optional): The function to be executed before the vscode is self-terminated.
    """

    def terminate_process():
        if post_execute is not None:
            post_execute()
            logger.info("Post execute function executed successfully!")
        if child_process.is_alive():
            child_process.terminate()
        child_process.join()

    logger = flytekit.current_context().logging
    start_time = time.time()
    check_interval = 60  # Interval for heartbeat checking in seconds
    last_heartbeat_check = time.time() - check_interval

    logger.info("waiting for task to resume...")
    while child_process.is_alive():
        current_time = time.time()
        if current_time - last_heartbeat_check >= check_interval:
            last_heartbeat_check = current_time
            if not os.path.exists(HEARTBEAT_PATH):
                delta = current_time - start_time
                logger.info(f"Code server has not been connected since {delta} seconds ago.")
                logger.info("Please open the browser to connect to the running server.")
            else:
                delta = current_time - os.path.getmtime(HEARTBEAT_PATH)
                logger.info(f"The latest activity on code server is {delta} seconds ago.")

            # If the time from last connection is longer than max idle seconds, terminate the vscode server.
            if delta > max_idle_seconds:
                logger.info(f"VSCode server is idle for more than {max_idle_seconds} seconds. Terminating...")
