"""
Unit tests for the EMR Serverless boto3 handler.

Tests the thin typed methods on :class:`EMRServerlessHandler` by patching
the single ``_call`` (and ``_paginate``) chokepoint that funnels all boto3
traffic.  This mirrors the flytekit-aws-sagemaker testing pattern
(``mock.patch("...Boto3ConnectorMixin._call")``).
"""

from unittest.mock import AsyncMock, patch

import pytest
from botocore.exceptions import ClientError

from flytekitplugins.awsemrserverless.boto_handler import EMRServerlessHandler


class TestEMRServerlessHandlerInit:
    def test_init_default(self):
        handler = EMRServerlessHandler()
        assert handler.region is None

    def test_init_with_region(self):
        handler = EMRServerlessHandler(region="us-west-2")
        assert handler.region == "us-west-2"


class TestEMRServerlessHandlerGetApplication:
    @pytest.mark.asyncio
    async def test_get_application_success(self, mock_call, mock_application_started):
        mock_call.return_value = mock_application_started

        handler = EMRServerlessHandler()
        result = await handler.get_application("00f5abc123def456")

        assert result["applicationId"] == "00f5abc123def456"
        assert result["state"] == "STARTED"
        mock_call.assert_called_once_with("get_application", applicationId="00f5abc123def456")

    @pytest.mark.asyncio
    async def test_get_application_not_found(self, mock_call):
        mock_call.side_effect = ClientError(
            {"Error": {"Code": "ResourceNotFoundException", "Message": "Not found"}},
            "GetApplication",
        )

        handler = EMRServerlessHandler()

        with pytest.raises(ClientError):
            await handler.get_application("nonexistent-app")


class TestEMRServerlessHandlerStartJobRun:
    @pytest.mark.asyncio
    async def test_start_job_run_success(self, mock_call):
        mock_call.return_value = {
            "applicationId": "app-123",
            "jobRunId": "job-456",
        }

        handler = EMRServerlessHandler()
        job_driver = {"sparkSubmit": {"entryPoint": "s3://bucket/main.py"}}

        job_run_id = await handler.start_job_run(
            application_id="app-123",
            execution_role_arn="arn:aws:iam::123456789012:role/Role",
            job_driver=job_driver,
        )

        assert job_run_id == "job-456"
        mock_call.assert_called_once()
        assert mock_call.call_args.args == ("start_job_run",)

    @pytest.mark.asyncio
    async def test_start_job_run_with_all_options(self, mock_call):
        mock_call.return_value = {
            "applicationId": "app-123",
            "jobRunId": "job-456",
        }

        handler = EMRServerlessHandler()
