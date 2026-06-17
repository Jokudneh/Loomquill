import json
import subprocess
from unittest.mock import MagicMock, patch

import pytest

from flytekit.clients.auth.authenticator import (
    ClientConfig,
    ClientCredentialsAuthenticator,
    CommandAuthenticator,
    DeviceCodeAuthenticator,
    PKCEAuthenticator,
    StaticClientConfigStore,
)
from flytekit.clients.auth.exceptions import AccessTokenNotFoundError, AuthenticationError
from flytekit.clients.auth.keyring import Credentials
from flytekit.clients.auth.token_client import DeviceCodeResponse

ENDPOINT = "example.com"

client_config = ClientConfig(
    token_endpoint="token_endpoint",
    authorization_endpoint="auth_endpoint",
    redirect_uri="redirect_uri",
    client_id="client",
)

static_cfg_store = StaticClientConfigStore(client_config)


@patch("flytekit.clients.auth.authenticator.KeyringStore")
@patch("flytekit.clients.auth.auth_client.AuthorizationClient.get_creds_from_remote")
@patch("flytekit.clients.auth.auth_client.AuthorizationClient.refresh_access_token")
def test_pkce_authenticator(mock_refresh: MagicMock, mock_get_creds: MagicMock, mock_keyring: MagicMock):
    mock_keyring.retrieve.return_value = None
    authn = PKCEAuthenticator(ENDPOINT, static_cfg_store)
    assert authn._verify is None

    authn = PKCEAuthenticator(ENDPOINT, static_cfg_store, verify=False)
    assert authn._verify is False

    assert authn._creds is None
    assert authn._auth_client is None
    authn.refresh_credentials()
    assert authn._auth_client
    mock_get_creds.assert_called()
    mock_refresh.assert_not_called()
    mock_keyring.store.assert_called()

    authn.refresh_credentials()
    mock_refresh.assert_called()


@patch("flytekit.clients.auth.authenticator.KeyringStore")
@patch("flytekit.clients.auth.auth_client.AuthorizationClient.get_creds_from_remote")
@patch("flytekit.clients.auth.auth_client.AuthorizationClient.refresh_access_token")
def test_pkce_refresh_failure_keeps_cached_credentials(
    mock_refresh: MagicMock, mock_get_creds: MagicMock, mock_keyring: MagicMock
):
    # A cached token exists, but refreshing it fails.
    mock_keyring.retrieve.return_value = Credentials("access", "refresh", ENDPOINT)
    mock_refresh.side_effect = AccessTokenNotFoundError("expired")

    authn = PKCEAuthenticator(ENDPOINT, static_cfg_store, verify=False)
    authn.refresh_credentials()

    # A failed refresh must not delete the cached credentials
    mock_keyring.delete.assert_not_called()
    mock_get_creds.assert_called_once()
    mock_keyring.store.assert_called()


@patch("subprocess.run")
def test_command_authenticator(mock_subprocess: MagicMock):
    with pytest.raises(AuthenticationError):
        authn = CommandAuthenticator(None)  # noqa

    authn = CommandAuthenticator(["echo"])

    authn.refresh_credentials()
    assert authn._creds
    mock_subprocess.assert_called()

    mock_subprocess.side_effect = subprocess.CalledProcessError(
        returncode=-1, cmd=["x"], output="some stdout output", stderr="Please run 'az login' to setup account"
