import ast
import inspect
import typing


def get_function_param_location(func: typing.Callable, param_name: str) -> (int, int):
    """
