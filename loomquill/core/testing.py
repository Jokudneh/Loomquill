import typing
from contextlib import contextmanager
from typing import Union
from unittest.mock import MagicMock

from flytekit.core.base_task import PythonTask
from flytekit.core.reference_entity import ReferenceEntity
from flytekit.core.workflow import WorkflowBase
from flytekit.loggers import logger


@contextmanager
def task_mock(t: PythonTask) -> typing.Generator[MagicMock, None, None]:
    """
    Use this method to mock a task declaration. It can mock any Task in Flytekit as long as it has a python native
