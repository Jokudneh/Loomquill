from unittest.mock import Mock

import grpc
import pytest

from flytekit.clients.grpc_utils.auth_interceptor import _ClientCallDetails
from flytekit.clients.grpc_utils.deadline_interceptor import (
    ScopedGrpcDeadlineInterceptor,
    get_scoped_grpc_deadline,
    scoped_grpc_deadline,
)
from flytekit.clients.grpc_utils.wrap_exception_interceptor import RetryExceptionWrapperInterceptor
from flytekit.exceptions.user import FlyteTimeout


class DeadlineExceededError(grpc.RpcError):
    def code(self):
        return grpc.StatusCode.DEADLINE_EXCEEDED

    def details(self):
        return "deadline exceeded"


def test_scoped_grpc_deadline_resets():
    assert get_scoped_grpc_deadline() is None
    with scoped_grpc_deadline(5):
        assert get_scoped_grpc_deadline() == 5
