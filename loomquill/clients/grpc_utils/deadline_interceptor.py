import contextlib
import contextvars
import typing

import grpc

from flytekit.clients.grpc_utils.auth_interceptor import _ClientCallDetails

_GRPC_DEADLINE_SECONDS: contextvars.ContextVar[typing.Optional[float]] = contextvars.ContextVar(
    "flytekit_grpc_deadline_seconds", default=None
)


def get_scoped_grpc_deadline() -> typing.Optional[float]:
    return _GRPC_DEADLINE_SECONDS.get()

