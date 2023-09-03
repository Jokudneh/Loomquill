import typing

from flytekit.exceptions.base import FlyteException as _FlyteException
from flytekit.exceptions.base import FlyteRecoverableException as _Recoverable

if typing.TYPE_CHECKING:
    from flytekit.core.base_task import Task
    from flytekit.core.workflow import WorkflowBase


class FlyteUserException(_FlyteException):
    _ERROR_CODE = "USER:Unknown"


class FlyteUserRuntimeException(_FlyteException):
    _ERROR_CODE = "USER:RuntimeError"

    def __init__(self, exc_value: Exception, timestamp: typing.Optional[float] = None):
        """
        FlyteUserRuntimeException is thrown when a user code raises an exception.

        :param exc_value: The exception that was raised from user code.
        :param timestamp: The timestamp as fractional seconds since epoch when the exception was raised.
        """
        self._exc_value = exc_value
        super().__init__(str(exc_value), timestamp=timestamp)

    @property
    def value(self):
        return self._exc_value

    @property
    def error_code(self):
        code = None
        if hasattr(self.value, "error_code"):
            code = self.value.error_code
        elif hasattr(type(self.value), "error_code"):
            code = type(self.value).error_code

        if code is None:
            return self._ERROR_CODE
        if isinstance(code, str):
            return code
        if isinstance(code, int):
            return str(code)
        raise _FlyteException(f"error_code must be a str or int, got {type(code).__name__}")


class FlyteTypeException(FlyteUserException, TypeError):
    _ERROR_CODE = "USER:TypeError"

    @staticmethod
    def _is_a_container(value):
        return isinstance(value, list) or isinstance(value, tuple) or isinstance(value, set)

    @classmethod
