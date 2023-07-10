"""Tests for Databricks PAT and OAuth M2M authentication."""

import http
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiohttp import ClientSession
from aioresponses import aioresponses

from flytekitplugins.spark.databricks_auth import (
    DEFAULT_OIDC_AUDIENCE,
    DEFAULT_OAUTH_SECRET_NAME,
    DATABRICKS_ENABLED_LABEL_SELECTOR,
    DatabricksAuthError,
    OIDCConnectorAuth,
    OIDCNamespaceServiceAccountAuth,
    OAuthM2MAuth,
    PATAuth,
    _DiscoveredOIDCConfig,
    _NAMESPACE_DISCOVERY_CACHE,
    _TokenCache,
    _Settings,
    _discover_namespace_oidc_sa,
    _discover_namespace_oidc_sa_sync,
    _post_token,
    _request_service_account_token,
    _resolve_oidc_token_file,
    build_auth,
    select_auth,
)


def _task_template(**custom):
    task_template = MagicMock()
    task_template.custom = custom
    return task_template


def _service_account(name, client_id=None, audience=None):
    annotations = {}
    if client_id is not None:
        annotations["flyte.org/databricks-client-id"] = client_id
    if audience is not None:
        annotations["flyte.org/databricks-audience"] = audience
    service_account = MagicMock()
    service_account.metadata.name = name
    service_account.metadata.annotations = annotations or None
    return service_account


@pytest.fixture(autouse=True)
def _clear_auth_environment(monkeypatch):
    for name in (
        "FLYTE_DATABRICKS_AUTH_TYPE",
        "FLYTE_DATABRICKS_OAUTH_SECRET_NAME",
        "FLYTE_DATABRICKS_OIDC_TOKEN_FILE",
        "FLYTE_DATABRICKS_OIDC_AUDIENCE",
        "DATABRICKS_CLIENT_ID",
        "DATABRICKS_CLIENT_SECRET",
        "AWS_WEB_IDENTITY_TOKEN_FILE",
    ):
        monkeypatch.delenv(name, raising=False)


def test_settings_use_default_secret_name():
    settings = _Settings.from_task(task_template=None, namespace="project-a")

    assert settings.token_secret_name is None
    assert settings.oauth_secret_name == DEFAULT_OAUTH_SECRET_NAME
    assert settings.namespace == "project-a"


def test_settings_use_task_secret_name():
    task_template = _task_template()
    task_template.custom["databricksTokenSecret"] = "custom-token"

    settings = _Settings.from_task(task_template=task_template, namespace="project-a")

    assert settings.token_secret_name == "custom-token"


@pytest.mark.asyncio
async def test_select_auth_returns_pat_by_default():
    task_template = _task_template()
    auth = await select_auth(
        task_template=task_template,
        workspace_url="example.cloud.databricks.com",
        namespace="project-a",
    )

    assert isinstance(auth, PATAuth)
    assert auth.auth_type == "pat"


@pytest.mark.asyncio
async def test_pat_auth_delegates_to_existing_token_lookup():
    task_template = _task_template()
    settings = _Settings(
        task_template=task_template,
        auth_type="pat",
        client_id=None,
        oauth_secret_name=DEFAULT_OAUTH_SECRET_NAME,
        token_secret_name="custom-token",
        oidc_token_file=None,
        oidc_audience=DEFAULT_OIDC_AUDIENCE,
        namespace="project-a",
    )
    auth = PATAuth("example.cloud.databricks.com", settings)

    with patch(
        "flytekitplugins.spark.connector.get_databricks_token",
        return_value="example-token",
    ) as get_token:
        token = await auth.get_bearer_token(AsyncMock())

    assert token == "example-token"
    get_token.assert_called_once_with(
        namespace="project-a",
        task_template=task_template,
        secret_name="custom-token",
    )


@pytest.mark.asyncio
async def test_select_auth_uses_explicit_m2m():
    auth = await select_auth(
        task_template=_task_template(databricksAuthType="oauth_m2m"),
        workspace_url="example.cloud.databricks.com",
        namespace="project-a",
    )

    assert isinstance(auth, OAuthM2MAuth)


@pytest.mark.asyncio
async def test_select_auth_rejects_unknown_type():
    with pytest.raises(DatabricksAuthError, match="Invalid Databricks auth type"):
        await select_auth(
            task_template=_task_template(databricksAuthType="unknown"),
            workspace_url="example.cloud.databricks.com",
            namespace="project-a",
        )


@pytest.mark.asyncio
async def test_m2m_uses_environment_credentials(monkeypatch):
    monkeypatch.setenv("DATABRICKS_CLIENT_ID", "example-client")
    monkeypatch.setenv("DATABRICKS_CLIENT_SECRET", "example-secret")
    auth = build_auth("example.cloud.databricks.com", "oauth_m2m")

    with aioresponses() as mocked:
        mocked.post(
            "https://example.cloud.databricks.com/oidc/v1/token",
            status=200,
            payload={"access_token": "example-access-token", "expires_in": 3600},
        )
        async with ClientSession() as session:
            token = await auth.get_bearer_token(session)

    assert token == "example-access-token"


@pytest.mark.asyncio
async def test_namespace_secret_overrides_environment(monkeypatch):
    monkeypatch.setenv("DATABRICKS_CLIENT_ID", "environment-client")
    monkeypatch.setenv("DATABRICKS_CLIENT_SECRET", "environment-secret")
    auth = build_auth(
        "namespace.cloud.databricks.com",
        "oauth_m2m",
        namespace="project-a",
    )

    def _secret(secret_name, secret_key, namespace):
        assert secret_name == DEFAULT_OAUTH_SECRET_NAME
        assert namespace == "project-a"
        return {
            "client_id": "namespace-client",
            "client_secret": "namespace-secret",
        }[secret_key]

    posted = {}

    async def _capture(session, workspace_url, form):
        posted.update(form)
        return {"access_token": "namespace-access-token", "expires_in": 3600}

    with patch(
        "flytekitplugins.spark.connector.get_secret_from_k8s",
        side_effect=_secret,
    ), patch(
