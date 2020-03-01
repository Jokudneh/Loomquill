import typing
from typing import Union

import grpc

from flytekit.exceptions.base import FlyteException
from flytekit.exceptions.system import FlyteSystemException, FlyteSystemUnavailableException
from flytekit.exceptions.user import (
    FlyteAuthenticationException,
    FlyteEntityAlreadyExistsException,
    FlyteEntityNotExistException,
    FlyteInvalidInputException,
    FlyteTimeout,
)


class RetryExceptionWrapperInterceptor(grpc.UnaryUnaryClientInterceptor, grpc.UnaryStreamClientInterceptor):
    def __init__(self, max_retries: int = 3):
        self._max_retries = max_retries

