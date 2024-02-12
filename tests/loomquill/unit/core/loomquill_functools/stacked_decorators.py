"""Script used for testing local execution of functool.wraps-wrapped tasks for stacked decorators"""

import os
from functools import wraps

from flytekit import task, workflow


def task_decorator_1(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        print("running task_decorator_1")
        return fn(*args, **kwargs)

    return wrapper


def task_decorator_2(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        print("running task_decorator_2")
        return fn(*args, **kwargs)

    return wrapper


def task_decorator_3(fn):
    @wraps(fn)
