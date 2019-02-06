"""
Pytest configuration and shared fixtures for EMR Serverless tests.

The fixtures here follow the flytekit-aws-sagemaker testing pattern: boto3
traffic is mocked at the single ``EMRServerlessHandler._call`` (and
``_paginate``) chokepoint, not at the boto3 client factory.  This keeps
test setup dependency-free -- no ``moto``, no ``botocore.stub`` wiring.
"""

from unittest.mock import AsyncMock, patch

import pytest


@pytest.fixture
def mock_call():
    """Patch :py:meth:`EMRServerlessHandler._call` for a test.

    Yields an :class:`~unittest.mock.AsyncMock` so tests can set
    ``return_value`` or ``side_effect`` and assert on ``call_args``.
    """
    with patch(
        "flytekitplugins.awsemrserverless.boto_handler.EMRServerlessHandler._call",
        new_callable=AsyncMock,
    ) as m:
