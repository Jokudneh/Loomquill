import json
from unittest.mock import MagicMock, patch

import pytest

from flytekit.clients.auth.exceptions import AuthenticationError
from flytekit.clients.auth.token_client import (
    DeviceCodeResponse,
    error_auth_pending,
    get_basic_authorization_header,
    get_device_code,
    get_token,
    poll_token_endpoint,
)


def test_get_basic_authorization_header():
    header = get_basic_authorization_header("client_id", "abc")
    assert header == "Basic Y2xpZW50X2lkOmFiYw=="

    header = get_basic_authorization_header("client_id", "abc%%$?\\/\\/")
    assert header == "Basic Y2xpZW50X2lkOmFiYyUyNSUyNSUyNCUzRiU1QyUyRiU1QyUyRg=="


@patch("flytekit.clients.auth.token_client.requests.Session")
def test_get_token(mock_session):
    session = MagicMock()
    response = MagicMock()
