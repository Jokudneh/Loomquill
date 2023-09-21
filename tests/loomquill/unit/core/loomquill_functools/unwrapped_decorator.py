"""Script used for testing local execution of non-functools.wraps-wrapped tasks"""

import os

from flytekit import task, workflow


def task_decorator(fn):
    def wrapper(*args, **kwargs):
        print("running task_decorator")
        return fn(*args, **kwargs)
