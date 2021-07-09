"""Script used for testing local execution of functool.wraps-wrapped tasks"""

from functools import wraps

from flytekit import task, workflow


def task_decorator(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)
