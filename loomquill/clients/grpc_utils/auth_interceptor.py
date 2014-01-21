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
