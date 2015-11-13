import re
from typing import Any, Dict, Optional, Tuple, Type, TypeVar

from flytekit.core.base_task import PythonTask, TaskMetadata
from flytekit.core.interface import Interface

T = TypeVar("T")


class SQLTask(PythonTask[T]):
    """
    Base task types for all SQL tasks. See `flytekit.extras.sqlite3.task.SQLite3Task`
    and `flytekitplugins.athena.task.AthenaTask` for examples of how to use it as a base class.

