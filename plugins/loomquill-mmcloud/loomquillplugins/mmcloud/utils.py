import asyncio
import shlex
import subprocess
from asyncio.subprocess import PIPE
from decimal import ROUND_CEILING, Decimal
from typing import Optional, Tuple

from flyteidl.core.execution_pb2 import TaskExecution
from kubernetes.utils.quantity import parse_quantity

from flytekit.core.resources import Resources

MMCLOUD_STATUS_TO_FLYTE_PHASE = {
    "Submitted": TaskExecution.RUNNING,
    "Initializing": TaskExecution.RUNNING,
    "Starting": TaskExecution.RUNNING,
    "Executing": TaskExecution.RUNNING,
    "Capturing": TaskExecution.RUNNING,
    "Floating": TaskExecution.RUNNING,
    "Suspended": TaskExecution.RUNNING,
    "Suspending": TaskExecution.RUNNING,
    "Resuming": TaskExecution.RUNNING,
    "Completed": TaskExecution.SUCCEEDED,
    "Cancelled": TaskExecution.FAILED,
    "Cancelling": TaskExecution.FAILED,
    "FailToComplete": TaskExecution.FAILED,
    "FailToExecute": TaskExecution.FAILED,
    "CheckpointFailed": TaskExecution.FAILED,
