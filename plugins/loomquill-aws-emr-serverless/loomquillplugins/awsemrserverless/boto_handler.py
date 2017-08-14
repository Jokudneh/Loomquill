"""
Boto3 helper for EMR Serverless API operations.

Provides a thin async wrapper around the boto3 EMR Serverless client, with
application-lifecycle management used by the connector.

All outbound boto3 traffic is funneled through two private helpers so that
tests can mock the entire handler at a single boundary (matches the
flytekit-aws-sagemaker ``Boto3ConnectorMixin._call`` pattern):

* :py:meth:`EMRServerlessHandler._call` -- single-shot API calls
* :py:meth:`EMRServerlessHandler._paginate` -- paginated list operations
"""

import asyncio
import logging
import time
from typing import Any, Dict, List, Optional

import boto3
from botocore.config import Config as BotoConfig
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

_BOTO_RETRY_CONFIG = BotoConfig(retries={"max_attempts": 3, "mode": "adaptive"})

_APP_STARTED = "STARTED"
_APP_TERMINAL = {"TERMINATED"}
_APP_NEEDS_START = {"CREATED", "STOPPED"}
_APP_TRANSITIONING = {"CREATING", "STARTING"}

_JOB_TERMINAL = {"SUCCESS", "FAILED", "CANCELLED"}


class EMRServerlessHandler:
    """
    Async-friendly wrapper around the boto3 EMR Serverless client.

    Retries are handled by botocore's built-in adaptive retry mode.
    Blocking boto3 calls are offloaded to a thread-pool executor so they
    do not block the asyncio event loop.
    """

    def __init__(self, region: Optional[str] = None):
        self.region = region
        self._client: Optional[Any] = None
        logger.debug("EMRServerlessHandler initialized: region=%s", region or "(default)")

    @property
    def client(self) -> Any:
        if self._client is None:
            kwargs: Dict[str, Any] = {
                "service_name": "emr-serverless",
                "config": _BOTO_RETRY_CONFIG,
            }
            if self.region:
                kwargs["region_name"] = self.region
            self._client = boto3.client(**kwargs)
            logger.debug(
                "Boto3 EMR Serverless client created: region=%s",
                self._client.meta.region_name,
            )
        return self._client

    async def _call(self, method: str, **params: Any) -> Dict[str, Any]:
        """Invoke a boto3 EMR Serverless client method in the thread-pool executor.

        This is the single chokepoint for all non-paginated boto3 API calls
        (``method`` is the boto3 client method name and ``params`` are keyword
        arguments forwarded to the call in the camelCase form the AWS SDK
        expects). Tests can mock the entire handler surface by patching just
        this method. Returns the raw response dict from the boto3 call.
        """
        func = getattr(self.client, method)
        loop = asyncio.get_event_loop()
