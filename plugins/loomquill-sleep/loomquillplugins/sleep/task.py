from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional

from flytekit.configuration import SerializationSettings
from flytekit.core.python_function_task import PythonFunctionTask
from flytekit.core.task import TaskPlugins


@dataclass
class Sleep:
    """
    Route a task to the backend ``core-sleep`` plugin.

    The sleep duration is provided as a normal task input, not plugin config.
    No container is launched; the backend handles the sleep directly.

    Usage::

