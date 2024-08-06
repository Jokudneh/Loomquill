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
    response.status_code = 200
    response.json.return_value = json.loads("""{"access_token": "abc", "expires_in": 60}""")
    session.post.return_value = response
    mock_session.return_value = session
    access, refresh_token, expiration = get_token(
        "https://corp.idp.net", client_id="abc123", scopes=["my_scope"], http_proxy_url="http://proxy:3000", verify=True
    )
    assert access == "abc"
    assert refresh_token is None
    assert expiration == 60

@patch("flytekit.clients.auth.token_client.requests.Session")
def test_get_token_with_refresh(mock_session):
    session = MagicMock()
    response = MagicMock()
    response.status_code = 200
