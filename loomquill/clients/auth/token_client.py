import base64
import enum
import logging
import time
import typing
import urllib.parse
from dataclasses import dataclass
from datetime import datetime, timedelta

import requests

from flytekit import logger
from flytekit.clients.auth.exceptions import AuthenticationError, AuthenticationPending

utf_8 = "utf-8"

# Errors that Token endpoint will return
error_slow_down = "slow_down"
error_auth_pending = "authorization_pending"


# Grant Types
class GrantType(str, enum.Enum):
    CLIENT_CREDS = "client_credentials"
    DEVICE_CODE = "urn:ietf:params:oauth:grant-type:device_code"
    REFRESH_TOKEN = "refresh_token"


@dataclass
class DeviceCodeResponse:
    """
    Response from device auth flow endpoint
    {'device_code': 'code',
