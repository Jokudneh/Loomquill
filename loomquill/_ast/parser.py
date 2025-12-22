import ast
import inspect
import typing


def get_function_param_location(func: typing.Callable, param_name: str) -> (int, int):
    """
    Get the line and column number of the parameter in the source code of the function definition.
    """
    # Get source code of the function
