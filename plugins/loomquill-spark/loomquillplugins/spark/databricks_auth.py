"""Authentication strategies for the Databricks connector.

PAT remains the default for backward compatibility. OAuth machine-to-machine
(M2M) authentication is opt-in through ``FLYTE_DATABRICKS_AUTH_TYPE`` or the
equivalent per-task setting.
"""

import asyncio
import json
import logging
import os
import random
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

from flytekit import lazy_module
from flytekit.models.task import TaskTemplate

aiohttp = lazy_module("aiohttp")

logger = logging.getLogger(__name__)

FLYTE_DATABRICKS_AUTH_TYPE_ENV = "FLYTE_DATABRICKS_AUTH_TYPE"
FLYTE_DATABRICKS_OAUTH_SECRET_NAME_ENV = "FLYTE_DATABRICKS_OAUTH_SECRET_NAME"
FLYTE_DATABRICKS_OIDC_TOKEN_FILE_ENV = "FLYTE_DATABRICKS_OIDC_TOKEN_FILE"
FLYTE_DATABRICKS_OIDC_AUDIENCE_ENV = "FLYTE_DATABRICKS_OIDC_AUDIENCE"
DATABRICKS_CLIENT_ID_ENV = "DATABRICKS_CLIENT_ID"
DATABRICKS_CLIENT_SECRET_ENV = "DATABRICKS_CLIENT_SECRET"
AWS_WEB_IDENTITY_TOKEN_FILE_ENV = "AWS_WEB_IDENTITY_TOKEN_FILE"

LABEL_DATABRICKS_ENABLED = "flyte.org/databricks-enabled"
ANNOTATION_DATABRICKS_CLIENT_ID = "flyte.org/databricks-client-id"
ANNOTATION_DATABRICKS_AUDIENCE = "flyte.org/databricks-audience"
DATABRICKS_ENABLED_LABEL_SELECTOR = f"{LABEL_DATABRICKS_ENABLED}=true"

DEFAULT_OAUTH_SECRET_NAME = "databricks-oauth"
DEFAULT_OIDC_AUDIENCE = "databricks"
DEFAULT_PROJECTED_SA_TOKEN_PATH = "/var/run/secrets/databricks/token"
NAMESPACE_DISCOVERY_CACHE_TTL_SECONDS = 300
TOKEN_REFRESH_BUFFER_SECONDS = 60
TOKEN_ENDPOINT_MAX_RETRIES = 3
TOKEN_ENDPOINT_BACKOFF_BASE_SECONDS = 0.2
VALID_AUTH_TYPES = {"pat", "oauth_m2m", "oidc_federation"}


class DatabricksAuthError(Exception):
    """Raised when Databricks authentication cannot be obtained."""


@dataclass
class _Settings:
    """Authentication settings resolved for one Databricks task."""

    task_template: Optional[TaskTemplate]
    auth_type: Optional[str]
    client_id: Optional[str]
    oauth_secret_name: str
    token_secret_name: Optional[str]
    oidc_token_file: Optional[str]
    oidc_audience: str
    namespace: Optional[str]

    @staticmethod
    def from_task(task_template: Optional[TaskTemplate], namespace: Optional[str]) -> "_Settings":
        custom: Dict[str, Any] = task_template.custom if task_template is not None else {}

        def _pick(task_key: str, env_key: Optional[str], default: Optional[str] = None) -> Optional[str]:
            task_value = custom.get(task_key)
            if task_value:
                return task_value
            if env_key:
                env_value = os.getenv(env_key)
                if env_value:
                    return env_value
            return default

        return _Settings(
            task_template=task_template,
            auth_type=_pick("databricksAuthType", FLYTE_DATABRICKS_AUTH_TYPE_ENV),
            client_id=_pick("databricksClientId", DATABRICKS_CLIENT_ID_ENV),
            oauth_secret_name=_pick(
                "databricksOauthSecret",
                FLYTE_DATABRICKS_OAUTH_SECRET_NAME_ENV,
                DEFAULT_OAUTH_SECRET_NAME,
            )
            or DEFAULT_OAUTH_SECRET_NAME,
            token_secret_name=custom.get("databricksTokenSecret"),
            oidc_token_file=_pick(
                "databricksOidcTokenFile",
                FLYTE_DATABRICKS_OIDC_TOKEN_FILE_ENV,
            ),
            oidc_audience=_pick(
                "databricksOidcAudience",
                FLYTE_DATABRICKS_OIDC_AUDIENCE_ENV,
                DEFAULT_OIDC_AUDIENCE,
            )
            or DEFAULT_OIDC_AUDIENCE,
            namespace=namespace,
        )


def _resolve_oidc_token_file(settings: _Settings) -> Optional[str]:
    """Resolve the first configured projected JWT file that exists."""
    candidates = (
        settings.oidc_token_file,
        os.getenv(AWS_WEB_IDENTITY_TOKEN_FILE_ENV),
        DEFAULT_PROJECTED_SA_TOKEN_PATH,
    )
    return next((path for path in candidates if path and os.path.exists(path)), None)


@dataclass
class _CachedToken:
    access_token: str
    refresh_at: float


class _TokenCache:
    """Async-safe in-memory cache for short-lived OAuth tokens."""

    def __init__(self) -> None:
        self._store: Dict[Tuple[str, str, str], _CachedToken] = {}
        self._lock = asyncio.Lock()

    async def get(self, key: Tuple[str, str, str]) -> Optional[str]:
        async with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            if entry.refresh_at <= time.time():
                self._store.pop(key, None)
                return None
            return entry.access_token

    async def put(self, key: Tuple[str, str, str], access_token: str, expires_in: int) -> None:
        async with self._lock:
            refresh_after = max(int(expires_in) - TOKEN_REFRESH_BUFFER_SECONDS, 0)
            self._store[key] = _CachedToken(
                access_token=access_token,
                refresh_at=time.time() + refresh_after,
            )

    async def invalidate(self, key: Tuple[str, str, str]) -> None:
        async with self._lock:
            self._store.pop(key, None)


_TOKEN_CACHE = _TokenCache()


@dataclass
class _DiscoveredOIDCConfig:
    service_account: str
    client_id: str
    audience: str


@dataclass
class _CachedDiscovery:
    config: Optional[_DiscoveredOIDCConfig]
    expires_at: float


class _NamespaceDiscoveryCache:
    """Cache namespace ServiceAccount discovery results, including misses."""

    def __init__(self) -> None:
        self._store: Dict[str, _CachedDiscovery] = {}
        self._lock = asyncio.Lock()

    async def get(self, namespace: str) -> Tuple[bool, Optional[_DiscoveredOIDCConfig]]:
        async with self._lock:
            entry = self._store.get(namespace)
            if entry is None or entry.expires_at <= time.time():
                self._store.pop(namespace, None)
                return False, None
            return True, entry.config

    async def put(
        self,
        namespace: str,
        config: Optional[_DiscoveredOIDCConfig],
    ) -> None:
        async with self._lock:
