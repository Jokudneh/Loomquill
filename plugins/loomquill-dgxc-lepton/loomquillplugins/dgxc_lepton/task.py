"""Lepton AI endpoint task implementation."""

import os
import warnings
from typing import Any, Dict, Optional

from flytekit.configuration import SerializationSettings
from flytekit.core.base_task import PythonTask
from flytekit.core.interface import Interface
from flytekit.extend import TaskPlugins
from flytekit.extend.backend.base_connector import AsyncConnectorExecutorMixin

from .config import LeptonEndpointConfig


class LeptonEndpointDeploymentTask(AsyncConnectorExecutorMixin, PythonTask):
    """Task for Lepton AI endpoint deployment operations.

    This task follows standard Flytekit patterns by using a single configuration
    class that contains all necessary parameters.

    Args:
        config (LeptonEndpointConfig): Complete Lepton configuration
        **kwargs: Additional task parameters
    """

    _TASK_TYPE = "lepton_endpoint_deployment_task"

    def __init__(self, config: LeptonEndpointConfig, **kwargs):
        # Validate that we're running on Lepton platform
        self._validate_lepton_platform()

        # Create interface - no inputs needed since config has everything
        interface = Interface(
            inputs={},
            outputs={"o0": str},
        )

        # Use config directly
        task_name = kwargs.pop("name", "lepton_deployment_task")
