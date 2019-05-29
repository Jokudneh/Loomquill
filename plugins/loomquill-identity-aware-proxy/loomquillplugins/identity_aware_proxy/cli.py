import logging
import os
import typing

import click
import jwt
from google.api_core.exceptions import NotFound
from google.auth import default
from google.auth.transport.requests import Request
from google.cloud import secretmanager
from google.oauth2 import id_token

from flytekit.clients.auth.auth_client import AuthorizationClient
from flytekit.clients.auth.authenticator import Authenticator
from flytekit.clients.auth.exceptions import AccessTokenNotFoundError
from flytekit.clients.auth.keyring import Credentials, KeyringStore

WEBAPP_CLIENT_ID_HELP = (
    "Webapp type OAuth 2.0 client ID used by the IAP. "
    "Typically in the form of `<xyz>.apps.googleusercontent.com`. "
    "Created when activating IAP for the Flyte deployment. "
    "https://cloud.google.com/iap/docs/enabling-kubernetes-howto#oauth-credentials"
)


class GCPIdentityAwareProxyAuthenticator(Authenticator):
    """
    This Authenticator encapsulates the entire OAauth 2.0 flow with GCP Identity Aware Proxy.

    The auth flow is described in https://cloud.google.com/iap/docs/authentication-howto#signing_in_to_the_application

    Automatically opens a browser window for login.
    """

    def __init__(
        self,
        audience: str,
        client_id: str,
        client_secret: str,
        verify: typing.Optional[typing.Union[bool, str]] = None,
    ):
        """
        Initialize with default creds from KeyStore using the audience name.
        """
        super().__init__(audience, "proxy-authorization", KeyringStore.retrieve(audience), verify=verify)
        self._auth_client = None

        self.audience = audience
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = "http://localhost:4444"

    def _initialize_auth_client(self):
        if not self._auth_client:
            self._auth_client = AuthorizationClient(
                endpoint=self.audience,
                # See step 3 in https://cloud.google.com/iap/docs/authentication-howto#signing_in_to_the_application
                auth_endpoint="https://accounts.google.com/o/oauth2/v2/auth",
                token_endpoint="https://oauth2.googleapis.com/token",
                # See step 3 in https://cloud.google.com/iap/docs/authentication-howto#signing_in_to_the_application
                scopes=["openid", "email"],
                client_id=self.client_id,
                redirect_uri=self.redirect_uri,
                verify=self._verify,
                # See step 3 in https://cloud.google.com/iap/docs/authentication-howto#signing_in_to_the_application
                request_auth_code_params={
                    "cred_ref": "true",
                    "access_type": "offline",
                },
                # See step 4 in https://cloud.google.com/iap/docs/authentication-howto#signing_in_to_the_application
                request_access_token_params={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "audience": self.audience,
                    "redirect_uri": self.redirect_uri,
                },
                # See https://cloud.google.com/iap/docs/authentication-howto#refresh_token
                refresh_access_token_params={
