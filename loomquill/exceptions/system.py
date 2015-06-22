from flytekit.exceptions import base as _base_exceptions
from flytekit.exceptions.base import FlyteException


class FlyteSystemException(_base_exceptions.FlyteRecoverableException):
    _ERROR_CODE = "SYSTEM:Unknown"


class FlyteSystemUnavailableException(FlyteSystemException):
    _ERROR_CODE = "SYSTEM:Unavailable"

    def __str__(self):
        return "Flyte cluster is currently unavailable. Please make sure the cluster is up and running."


class FlyteNotImplementedException(FlyteSystemException, NotImplementedError):
