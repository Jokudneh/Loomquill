"""Script used for testing local execution of functool.wraps-wrapped tasks"""
from __future__ import annotations

import os
from functools import wraps

from flytekit import task, workflow


def task_decorator(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        print(f"before running {fn.__name__}")
