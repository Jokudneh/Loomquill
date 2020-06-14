import logging
import ssl
import typing
from http import HTTPStatus
from importlib.metadata import entry_points

import grpc
import requests
from flyteidl.service.auth_pb2 import OAuth2MetadataRequest, PublicClientAuthConfigRequest
from flyteidl.service.auth_pb2_grpc import AuthMetadataServiceStub

from flytekit.clients.auth.authenticator import (
    Authenticator,
    ClientConfig,
    ClientConfigStore,
    ClientCredentialsAuthenticator,
    CommandAuthenticator,
    DeviceCodeAuthenticator,
    PKCEAuthenticator,
)
from flytekit.clients.grpc_utils.auth_interceptor import AuthUnaryInterceptor
from flytekit.clients.grpc_utils.deadline_interceptor import ScopedGrpcDeadlineInterceptor
from flytekit.clients.grpc_utils.default_metadata_interceptor import DefaultMetadataInterceptor
from flytekit.clients.grpc_utils.wrap_exception_interceptor import RetryExceptionWrapperInterceptor
from flytekit.configuration import AuthType, PlatformConfig

AUTH_ENTRY_POINT_GROUP = "flytekit.auth"

_authenticator_registry: dict[str, typing.Callable[["PlatformConfig", ClientConfigStore], Authenticator]] = {}


def register_authenticator_plugin(
    name: str,
    factory: typing.Callable[["PlatformConfig", ClientConfigStore], Authenticator],
) -> None:
    """Register an authenticator factory by name.

    This is the primary registration mechanism and works in every environment
    (pip, Bazel, mono-repo vendoring, etc.).  Entry-point discovery is attempted
    as a fallback when no explicit registration exists.

    Example::

        from flytekit.clients.auth_helper import register_authenticator_plugin
        register_authenticator_plugin("gcp_id_token", GcpIdTokenAuthenticator)
    """
    _authenticator_registry[name.lower()] = factory


class RemoteClientConfigStore(ClientConfigStore):
    """
    This class implements the ClientConfigStore that is served by the Flyte Server, that implements AuthMetadataService
    """

    def __init__(self, secure_channel: grpc.Channel):
        self._secure_channel = secure_channel

    def get_client_config(self) -> ClientConfig:
        """
        Retrieves the ClientConfig from the given grpc.Channel assuming  AuthMetadataService is available
        """
        metadata_service = AuthMetadataServiceStub(self._secure_channel)
        public_client_config = metadata_service.GetPublicClientConfig(PublicClientAuthConfigRequest())
        oauth2_metadata = metadata_service.GetOAuth2Metadata(OAuth2MetadataRequest())
        return ClientConfig(
            token_endpoint=oauth2_metadata.token_endpoint,
            authorization_endpoint=oauth2_metadata.authorization_endpoint,
            redirect_uri=public_client_config.redirect_uri,
            client_id=public_client_config.client_id,
            scopes=public_client_config.scopes,
            header_key=public_client_config.authorization_metadata_key or None,
            device_authorization_endpoint=oauth2_metadata.device_authorization_endpoint,
            audience=public_client_config.audience,
        )


def _load_authenticator_plugin(
    auth_type_name: str, cfg: "PlatformConfig", cfg_store: ClientConfigStore
) -> typing.Optional[Authenticator]:
    """Load an authenticator by name (case-insensitive).

    Resolution order:

    1. Explicit registry (populated via :func:`register_authenticator_plugin`).
    2. ``importlib.metadata`` entry-point group ``flytekit.auth``.

    Names are compared in lowercase so that ``GCP_ID_TOKEN``,
    ``gcp_id_token``, and ``Gcp_Id_Token`` all resolve to the same plugin.

    The loaded object must be a callable (class or factory function) with the
    signature ``(PlatformConfig, ClientConfigStore) -> Authenticator``.
    """
    name_lower = auth_type_name.lower()

    factory = _authenticator_registry.get(name_lower)
    if factory is not None:
        logging.info(f"Using registered auth plugin '{name_lower}'")
        return factory(cfg, cfg_store)
