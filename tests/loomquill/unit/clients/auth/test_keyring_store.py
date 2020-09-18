from unittest.mock import MagicMock, patch

from keyring.errors import NoKeyringError

from flytekit.clients.auth.keyring import Credentials, KeyringStore

from flytekit.clients.auth_helper import upgrade_channel_to_authenticated, upgrade_channel_to_proxy_authenticated

from flytekit.configuration import PlatformConfig

import pytest

from flytekit.clients.auth.authenticator import CommandAuthenticator

from flytekit.clients.grpc_utils.auth_interceptor import AuthUnaryInterceptor

@patch("keyring.get_password")
def test_keyring_store_get(kr_get_password: MagicMock):
    kr_get_password.return_value = "t"
    assert KeyringStore.retrieve("example1.com") is not None

