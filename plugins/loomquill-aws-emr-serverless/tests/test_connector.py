"""
Unit tests for EMR Serverless Connector.
"""

import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from flyteidl.core.execution_pb2 import TaskExecution

from flytekitplugins.awsemrserverless import (
    EMRServerlessConnector,
    EMRServerlessJobMetadata,
)
from flytekit.extend.backend.utils import convert_to_flyte_phase

from flytekitplugins.awsemrserverless.connector import (
    EMR_SERVERLESS_STATES,
    _ENV_ALLOW_CREATE_APPLICATION,
    _ENV_APPLICATION_NAME_PREFIX,
)


def _make_handler(**overrides) -> AsyncMock:
    """Build a mock EMRServerlessHandler with sensible defaults."""
    handler = AsyncMock()
    handler.ensure_application_started = AsyncMock()
    handler.start_application_if_needed = AsyncMock(return_value=True)
    handler.start_job_run = AsyncMock(return_value="job-123")
    handler.create_application = AsyncMock(return_value="new-app-123")
    handler.get_application = AsyncMock(return_value={
        "applicationId": "00f5abc123def456",
        "state": "STARTED",
        "imageConfiguration": {},
    })
    handler.update_application = AsyncMock()
    handler.client.meta.region_name = "us-east-1"
    handler.region = "us-east-1"
    for k, v in overrides.items():
        setattr(handler, k, v)
    return handler


class TestEMRServerlessJobMetadata:
    def test_metadata_creation(self):
        metadata = EMRServerlessJobMetadata(
            application_id="app-123",
            job_run_id="job-456",
            region="us-east-1",
        )
        assert metadata.application_id == "app-123"
        assert metadata.job_run_id == "job-456"
        assert metadata.region == "us-east-1"
        assert metadata.created_application is False
        assert metadata.is_script_mode is False
        assert metadata.pending_job_request is None

    def test_metadata_with_created_app(self):
        metadata = EMRServerlessJobMetadata(
            application_id="app-123",
            job_run_id="job-456",
            region="us-west-2",
            created_application=True,
        )
        assert metadata.created_application is True

    def test_pending_metadata_round_trip(self):
        metadata = EMRServerlessJobMetadata(
            application_id="app-123",
            job_run_id="",
            region="us-east-1",
            is_script_mode=True,
            pending_job_request={
                "execution_role_arn": "arn:aws:iam::123456789012:role/Role",
                "job_driver": {"sparkSubmit": {"entryPoint": "s3://bucket/main.py"}},
                "client_token": "stable-token",
            },
        )

        decoded = EMRServerlessJobMetadata.decode(metadata.encode())

        assert decoded == metadata


class TestEMRServerlessConnector:
    def test_connector_initialization(self):
        connector = EMRServerlessConnector()
        assert connector.name == "EMR Serverless Connector"

    @pytest.mark.asyncio
    async def test_create_with_existing_application(self, sample_config):
        connector = EMRServerlessConnector()
        mock_handler = _make_handler()

        mock_template = MagicMock()
        mock_template.custom = sample_config.to_dict()
        mock_template.id = MagicMock()
        mock_template.id.name = "test-task"

        with patch.object(connector, "_get_handler", return_value=mock_handler):
            with patch.object(connector, "_extract_config", return_value=sample_config):
                metadata = await connector.create(mock_template)

        assert isinstance(metadata, EMRServerlessJobMetadata)
        assert metadata.application_id == sample_config.application_id
        assert metadata.job_run_id == "job-123"
        assert metadata.is_script_mode is True
        mock_handler.start_application_if_needed.assert_called_once()
        mock_handler.start_job_run.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_defers_job_submission_while_application_starts(self, sample_config):
        connector = EMRServerlessConnector()
        mock_handler = _make_handler()
        mock_handler.start_application_if_needed = AsyncMock(return_value=False)

        mock_template = MagicMock()
        mock_template.custom = sample_config.to_dict()
        mock_template.id = MagicMock()
        mock_template.id.name = "test-task"

        with patch.object(connector, "_get_handler", return_value=mock_handler):
            with patch.object(connector, "_extract_config", return_value=sample_config):
                metadata = await connector.create(mock_template)

        assert metadata.application_id == sample_config.application_id
        assert metadata.job_run_id == ""
        assert metadata.is_script_mode is True
        assert metadata.pending_job_request is not None
        assert metadata.pending_job_request["client_token"]
        mock_handler.start_job_run.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_with_new_application(self, sample_spark_job_driver):
        """application_name + env var true => create succeeds."""
        from flytekitplugins.awsemrserverless import EMRServerless

        config = EMRServerless(
            execution_role_arn="arn:aws:iam::123456789012:role/Role",
            spark_job_driver=sample_spark_job_driver,
            application_name="test-app",
            region="us-east-1",
        )

        connector = EMRServerlessConnector()
        mock_handler = _make_handler()

        mock_template = MagicMock()
        mock_template.custom = config.to_dict()
        mock_template.id = MagicMock()
        mock_template.id.name = "test-task"

        with patch.dict(os.environ, {_ENV_ALLOW_CREATE_APPLICATION: "true"}):
            with patch.object(connector, "_get_handler", return_value=mock_handler):
                with patch.object(connector, "_extract_config", return_value=config):
                    metadata = await connector.create(mock_template)

        assert metadata.application_id == "new-app-123"
        assert metadata.created_application is True
        mock_handler.create_application.assert_called_once()
        assert mock_handler.create_application.call_args.kwargs["name"] == "test-app"

    @pytest.mark.asyncio
    async def test_create_fails_no_app_id_no_app_name(self, sample_spark_job_driver):
        """Without application_id or application_name, create must fail."""
        from flytekitplugins.awsemrserverless import EMRServerless

        config = EMRServerless(
            execution_role_arn="arn:aws:iam::123456789012:role/Role",
            spark_job_driver=sample_spark_job_driver,
        )

        connector = EMRServerlessConnector()
        mock_handler = _make_handler()

        mock_template = MagicMock()
        mock_template.custom = config.to_dict()
        mock_template.id = MagicMock()
        mock_template.id.name = "test-task"

        with patch.dict(os.environ, {_ENV_ALLOW_CREATE_APPLICATION: "true"}):
            with patch.object(connector, "_get_handler", return_value=mock_handler):
                with patch.object(connector, "_extract_config", return_value=config):
                    with pytest.raises(ValueError, match="No application_id provided and no application_name"):
                        await connector.create(mock_template)

    @pytest.mark.asyncio
    async def test_create_blocked_by_connector_env_var(self, sample_spark_job_driver):
        """When connector env var is false (default), creation is blocked even with application_name."""
        from flytekitplugins.awsemrserverless import EMRServerless

        config = EMRServerless(
            execution_role_arn="arn:aws:iam::123456789012:role/Role",
            spark_job_driver=sample_spark_job_driver,
            application_name="my-app",
        )

        connector = EMRServerlessConnector()
        mock_handler = _make_handler()

        mock_template = MagicMock()
        mock_template.custom = config.to_dict()
        mock_template.id = MagicMock()
        mock_template.id.name = "test-task"

        with patch.dict(os.environ, {_ENV_ALLOW_CREATE_APPLICATION: "false"}):
            with patch.object(connector, "_get_handler", return_value=mock_handler):
                with patch.object(connector, "_extract_config", return_value=config):
                    with pytest.raises(ValueError, match="disabled by the connector"):
                        await connector.create(mock_template)

    @pytest.mark.asyncio
    async def test_create_blocked_when_env_var_unset(self, sample_spark_job_driver):
        """When the env var is not set, default is false => creation blocked."""
        from flytekitplugins.awsemrserverless import EMRServerless

        config = EMRServerless(
            execution_role_arn="arn:aws:iam::123456789012:role/Role",
            spark_job_driver=sample_spark_job_driver,
            application_name="my-app",
        )

        connector = EMRServerlessConnector()
        mock_handler = _make_handler()

        mock_template = MagicMock()
        mock_template.custom = config.to_dict()
        mock_template.id = MagicMock()
        mock_template.id.name = "test-task"

        env = os.environ.copy()
        env.pop(_ENV_ALLOW_CREATE_APPLICATION, None)
        with patch.dict(os.environ, env, clear=True):
            with patch.object(connector, "_get_handler", return_value=mock_handler):
                with patch.object(connector, "_extract_config", return_value=config):
                    with pytest.raises(ValueError, match="disabled by the connector"):
                        await connector.create(mock_template)

    @pytest.mark.asyncio
    async def test_create_applies_application_name_prefix(self, sample_spark_job_driver):
        """FLYTE_EMR_APPLICATION_NAME_PREFIX should be prepended to the app name."""
        from flytekitplugins.awsemrserverless import EMRServerless

        config = EMRServerless(
            execution_role_arn="arn:aws:iam::123456789012:role/Role",
            spark_job_driver=sample_spark_job_driver,
            application_name="my-etl-app",
            region="us-east-1",
        )

        connector = EMRServerlessConnector()
        mock_handler = _make_handler()

        mock_template = MagicMock()
        mock_template.custom = config.to_dict()
        mock_template.id = MagicMock()
        mock_template.id.name = "test-task"

        with patch.dict(os.environ, {
            _ENV_ALLOW_CREATE_APPLICATION: "true",
            _ENV_APPLICATION_NAME_PREFIX: "flyte-prod-",
        }):
            with patch.object(connector, "_get_handler", return_value=mock_handler):
                with patch.object(connector, "_extract_config", return_value=config):
                    await connector.create(mock_template)

        call_kwargs = mock_handler.create_application.call_args.kwargs
        assert call_kwargs["name"] == "flyte-prod-my-etl-app"

    @pytest.mark.asyncio
    async def test_create_no_double_prefix(self, sample_spark_job_driver):
        """If application_name already starts with the prefix, don't double-prefix."""
        from flytekitplugins.awsemrserverless import EMRServerless

        config = EMRServerless(
            execution_role_arn="arn:aws:iam::123456789012:role/Role",
            spark_job_driver=sample_spark_job_driver,
            application_name="flyte-prod-my-app",
            region="us-east-1",
        )

        connector = EMRServerlessConnector()
        mock_handler = _make_handler()

        mock_template = MagicMock()
        mock_template.custom = config.to_dict()
        mock_template.id = MagicMock()
        mock_template.id.name = "test-task"

        with patch.dict(os.environ, {
            _ENV_ALLOW_CREATE_APPLICATION: "true",
            _ENV_APPLICATION_NAME_PREFIX: "flyte-prod-",
        }):
            with patch.object(connector, "_get_handler", return_value=mock_handler):
                with patch.object(connector, "_extract_config", return_value=config):
                    await connector.create(mock_template)

        call_kwargs = mock_handler.create_application.call_args.kwargs
        assert call_kwargs["name"] == "flyte-prod-my-app"

    @pytest.mark.asyncio
    async def test_create_no_prefix_when_unset(self, sample_spark_job_driver):
        """Without the prefix env var, the application name is used as-is."""
        from flytekitplugins.awsemrserverless import EMRServerless

        config = EMRServerless(
            execution_role_arn="arn:aws:iam::123456789012:role/Role",
            spark_job_driver=sample_spark_job_driver,
            application_name="my-raw-name",
            region="us-east-1",
        )

        connector = EMRServerlessConnector()
        mock_handler = _make_handler()

        mock_template = MagicMock()
        mock_template.custom = config.to_dict()
        mock_template.id = MagicMock()
        mock_template.id.name = "test-task"

        env = os.environ.copy()
        env.pop(_ENV_APPLICATION_NAME_PREFIX, None)
        env[_ENV_ALLOW_CREATE_APPLICATION] = "true"
        with patch.dict(os.environ, env, clear=True):
            with patch.object(connector, "_get_handler", return_value=mock_handler):
                with patch.object(connector, "_extract_config", return_value=config):
                    await connector.create(mock_template)

        call_kwargs = mock_handler.create_application.call_args.kwargs
        assert call_kwargs["name"] == "my-raw-name"

    @pytest.mark.asyncio
    async def test_create_passes_architecture_and_scheduler(self, sample_spark_job_driver):
        """Verify new app-creation params are forwarded to the handler."""
        from flytekitplugins.awsemrserverless import EMRServerless

        config = EMRServerless(
            execution_role_arn="arn:aws:iam::123456789012:role/Role",
            spark_job_driver=sample_spark_job_driver,
            application_name="test-app",
            architecture="ARM64",
            scheduler_configuration={"maxConcurrentRuns": 5},
            auto_stop_config={"enabled": True, "idleTimeoutMinutes": 30},
            runtime_configuration=[{"classification": "spark-defaults", "properties": {"spark.executor.cores": "8"}}],
            region="us-east-1",
        )

        connector = EMRServerlessConnector()
        mock_handler = _make_handler()

        mock_template = MagicMock()
        mock_template.custom = config.to_dict()
        mock_template.id = MagicMock()
        mock_template.id.name = "test-task"

        with patch.dict(os.environ, {_ENV_ALLOW_CREATE_APPLICATION: "true"}):
            with patch.object(connector, "_get_handler", return_value=mock_handler):
                with patch.object(connector, "_extract_config", return_value=config):
                    await connector.create(mock_template)

        call_kwargs = mock_handler.create_application.call_args.kwargs
        assert call_kwargs["architecture"] == "ARM64"
        assert call_kwargs["scheduler_configuration"] == {"maxConcurrentRuns": 5}
        assert call_kwargs["auto_stop_config"] == {"enabled": True, "idleTimeoutMinutes": 30}
        assert call_kwargs["runtime_configuration"][0]["classification"] == "spark-defaults"
