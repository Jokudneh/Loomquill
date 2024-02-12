import logging
import typing
from dataclasses import dataclass

import keyring
from keyring.errors import NoKeyringError, PasswordDeleteError


@dataclass
class Credentials(object):
    """
    Stores the credentials together
    """

    access_token: str
    refresh_token: typing.Optional[str] = None
    for_endpoint: str = "flyte-default"
    expires_in: typing.Optional[int] = None
    id_token: typing.Optional[str] = None


class KeyringStore:
    """
    Methods to access Keyring Store.
    """

    _access_token_key = "access_token"
    _refresh_token_key = "refresh_token"
    _id_token_key = "id_token"

    @staticmethod
    def store(credentials: Credentials) -> Credentials:
        try:
            if credentials.refresh_token:
                keyring.set_password(
                    credentials.for_endpoint,
