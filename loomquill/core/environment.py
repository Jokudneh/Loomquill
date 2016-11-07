import copy
from functools import partial, wraps
from typing import Any, Callable, TypeVar, Union

from rich.console import Console
from rich.panel import Panel
from rich.pretty import Pretty
from typing_extensions import Concatenate, ParamSpec

from flytekit.core.dynamic_workflow_task import dynamic
from flytekit.core.task import task

P = ParamSpec("P")
T = TypeVar("T")


# basically, I want the docstring for `flyte.task` to be available for users to see
# this is "copying" the docstring from `flyte.task` to functions wrapped by `forge`
# more details here: https://github.com/python/typing/issues/270
def forge(source: Callable[Concatenate[Any, P], T]) -> Callable[[Callable], Callable[Concatenate[Any, P], T]]:
    def wrapper(target: Callable) -> Callable[Concatenate[Any, P], T]:
        @wraps(source)
        def wrapped(self, *args: P.args, **kwargs: P.kwargs) -> T:
            return target(self, *args, **kwargs)
