from http import HTTPStatus
from importlib.metadata import EntryPoint
from unittest.mock import MagicMock, patch

import pytest
import requests
from flyteidl.service.auth_pb2 import OAuth2MetadataResponse, PublicClientAuthConfigResponse

from flytekit.clients.auth.authenticator import (
    Authenticator,
    ClientConfig,
    ClientConfigStore,
    ClientCredentialsAuthenticator,
    CommandAuthenticator,
    DeviceCodeAuthenticator,
    PKCEAuthenticator,
)
from flytekit.clients.auth.exceptions import AuthenticationError
from flytekit.clients.auth.keyring import Credentials
from flytekit.clients.auth_helper import (
    AUTH_ENTRY_POINT_GROUP,
    RemoteClientConfigStore,
    _authenticator_registry,
    get_authenticator,
    get_session,
    register_authenticator_plugin,
    upgrade_channel_to_authenticated,
    upgrade_channel_to_proxy_authenticated,
    wrap_exceptions_channel,
)
from flytekit.clients.grpc_utils.auth_interceptor import AuthUnaryInterceptor
from flytekit.clients.grpc_utils.deadline_interceptor import ScopedGrpcDeadlineInterceptor
from flytekit.clients.grpc_utils.wrap_exception_interceptor import RetryExceptionWrapperInterceptor
from flytekit.configuration import AuthType, PlatformConfig

REDIRECT_URI = "http://localhost:53593/callback"

TOKEN_ENDPOINT = "https://your.domain.io/oauth2/token"

CLIENT_ID = "flytectl"

OAUTH_AUTHORIZE = "https://your.domain.io/oauth2/authorize"

DEVICE_AUTH_ENDPOINT = "https://your.domain.io/..."


def get_auth_service_mock() -> MagicMock:
    auth_stub_mock = MagicMock()
    auth_stub_mock.GetPublicClientConfig.return_value = PublicClientAuthConfigResponse(
        client_id=CLIENT_ID,
        redirect_uri=REDIRECT_URI,
        scopes=["offline", "all"],
        authorization_metadata_key="flyte-authorization",
    )
    auth_stub_mock.GetOAuth2Metadata.return_value = OAuth2MetadataResponse(
        issuer="https://your.domain.io",
