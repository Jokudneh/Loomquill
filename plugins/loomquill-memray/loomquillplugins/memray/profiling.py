import os
import sys
import time
from typing import Callable, List, Optional

import memray
from flytekit import Deck
from flytekit.core.utils import ClassDecorator


class memray_profiling(ClassDecorator):
    def __init__(
        self,
        task_function: Optional[Callable] = None,
        native_traces: bool = False,
        trace_python_allocators: bool = False,
        follow_fork: bool = False,
        memory_interval_ms: int = 10,
        memray_html_reporter: str = "flamegraph",
        memray_reporter_args: Optional[List[str]] = None,
    ):
        """Memray profiling plugin.
        Args:
            task_function (function, optional): The user function to be decorated. Defaults to None.
