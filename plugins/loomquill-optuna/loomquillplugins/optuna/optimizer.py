import asyncio
import inspect
from copy import copy, deepcopy
from dataclasses import dataclass
from types import SimpleNamespace
from typing import Any, Awaitable, Callable, Optional, Union

from typing_extensions import Concatenate, ParamSpec

import optuna
from flytekit.core.python_function_task import AsyncPythonFunctionTask
from flytekit.exceptions.eager import EagerException


class Suggestion: ...


class Number(Suggestion):
    def __post_init__(self):
        if self.low >= self.high:
            raise ValueError("low must be less than high")

        if self.step is not None and self.step > (self.high - self.low):
            raise ValueError("step must be less than the range of the suggestion")


@dataclass
class Float(Number):
    low: float
    high: float
    step: Optional[float] = None
    log: bool = False


@dataclass
class Integer(Number):
    low: int
    high: int
    step: int = 1
    log: bool = False


@dataclass
class Category(Suggestion):
    choices: list[Any]


suggest = SimpleNamespace(float=Float, integer=Integer, category=Category)

P = ParamSpec("P")

Result = Union[float, tuple[float, ...]]

CallbackType = Callable[Concatenate[optuna.Trial, P], Union[Awaitable[Result], Result]]


@dataclass
class Optimizer:
    objective: Union[CallbackType, AsyncPythonFunctionTask]
    concurrency: int
