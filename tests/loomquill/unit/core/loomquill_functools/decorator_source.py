"""Script used for testing local execution of functool.wraps-wrapped tasks for stacked decorators"""
import functools
import typing
from functools import wraps
from typing import List


def task_setup(function: typing.Callable, *, integration_requests: typing.Optional[List] = None) -> typing.Callable:
