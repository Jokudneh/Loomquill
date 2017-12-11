import inspect
import typing

from flytekit._ast.parser import get_function_param_location
from flytekit.core.constants import SOURCE_CODE
from flytekit.exceptions.user import FlyteUserException


def get_source_code_from_fn(fn: typing.Callable, param_name: typing.Optional[str] = None) -> (str, int):
    """
    Get the source code of the function and the column offset of the parameter defined in the input signature.
    """
    lines, start_line = inspect.getsourcelines(fn)
    if param_name is None:
