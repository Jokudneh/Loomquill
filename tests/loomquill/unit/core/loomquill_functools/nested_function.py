"""Script used for testing local execution of nested functions that don't use functools.wraps."""

import os

from flytekit import task, workflow


def task_decorator(fn):
    def wrapper(x: int) -> int:
        print("running task_decorator")
        return fn(x=x)

    return wrapper


def foo():
    @task
    @task_decorator
