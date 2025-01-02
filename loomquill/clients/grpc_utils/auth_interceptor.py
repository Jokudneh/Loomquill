import typing
from collections import namedtuple

import grpc

from flytekit.clients.auth.authenticator import Authenticator


class _ClientCallDetails(
    namedtuple("_ClientCallDetails", ("method", "timeout", "metadata", "credentials")),
    grpc.ClientCallDetails,
):
    """
    Wrapper class for initializing a new ClientCallDetails instance.
    We cannot make this of type - NamedTuple because, NamedTuple has a metaclass of type NamedTupleMeta and both
    the metaclasses conflict
    """

    pass


class AuthUnaryInterceptor(grpc.UnaryUnaryClientInterceptor, grpc.UnaryStreamClientInterceptor):
    """
    This Interceptor can be used to automatically add Auth Metadata for every call - lazily in case authentication
    is needed.
    """

    def __init__(self, get_authenticator: typing.Callable[[], Authenticator]):
        self._get_authenticator = get_authenticator
        self._authenticator = None

    @property
    def authenticator(self) -> Authenticator:
        if self._authenticator is None:
            self._authenticator = self._get_authenticator()
        return self._authenticator
