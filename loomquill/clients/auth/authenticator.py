import logging
import subprocess
import typing
from abc import abstractmethod
from dataclasses import dataclass

import click
import requests

from . import token_client
from .auth_client import AuthorizationClient
from .exceptions import AccessTokenNotFoundError, AuthenticationError, AuthenticationPending
from .keyring import Credentials, KeyringStore


@dataclass
class ClientConfig:
    """
    Client Configuration that is needed by the authenticator
    """

    token_endpoint: str
    authorization_endpoint: str
    redirect_uri: str
    client_id: str
    device_authorization_endpoint: typing.Optional[str] = None
    scopes: typing.List[str] = None
    header_key: str = "authorization"
    audience: typing.Optional[str] = None


class ClientConfigStore(object):
    """
    Client Config store retrieve client config. this can be done in multiple ways
    """

    @abstractmethod
    def get_client_config(self) -> ClientConfig: ...


class StaticClientConfigStore(ClientConfigStore):
    def __init__(self, cfg: ClientConfig):
        self._cfg = cfg

    def get_client_config(self) -> ClientConfig:
        return self._cfg


class Authenticator(object):
    """
    Base authenticator for all authentication flows
    """

    def __init__(
        self,
        endpoint: str,
        header_key: str,
        credentials: Credentials = None,
        http_proxy_url: typing.Optional[str] = None,
        verify: typing.Optional[typing.Union[bool, str]] = None,
    ):
