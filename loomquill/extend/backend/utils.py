import asyncio
import functools
import inspect
from typing import Callable, Coroutine

from flyteidl.core.execution_pb2 import TaskExecution

import flytekit
from flytekit.models.task import TaskTemplate


