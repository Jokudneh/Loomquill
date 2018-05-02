"""Optimized Lepton AI connector with improved performance and reduced redundancy."""

import asyncio
import re
import time
from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Dict, Optional

from flyteidl.admin.agent_pb2 import GetTaskLogsResponse
from flyteidl.core.execution_pb2 import TaskExecution, TaskLog
from leptonai.api.v1.deployment import DeploymentAPI
from leptonai.api.v1.log import LogAPI
from leptonai.api.v1.types.common import Metadata
from leptonai.api.v1.types.deployment import LeptonDeployment, LeptonDeploymentUserSpec
from leptonai.api.v2.client import APIClient

from flytekit import current_context
from flytekit.extend.backend.base_connector import AsyncConnectorBase, ConnectorRegistry, Resource, ResourceMeta
from flytekit.extend.backend.utils import convert_to_flyte_phase
from flytekit.loggers import logger
from flytekit.models.literals import LiteralMap
from flytekit.models.task import TaskTemplate


def log_info(message: str) -> None:
    """Optimized unified logging helper."""
    logger.info(message)
    print(message, flush=True)  # More efficient than separate flush call


@dataclass
class LeptonMetadata(ResourceMeta):
    deployment_name: str


class BaseLeptonConnector(AsyncConnectorBase):
    """Base class for Lepton connectors with shared functionality."""

    # Optimized class constants
    ORIGIN_URL = "https://gateway.dgxc-lepton.nvidia.com"

    # Consolidated status mapping with frozenset for faster lookup
    _PENDING_STATES = frozenset(["starting", "scaling", "updating", "not ready", "notready"])
    _SUCCESS_STATES = frozenset(["ready", "deleting", "stopping", "terminating", "stopped", "terminated"])
    _FAILED_STATES = frozenset(["unknown", "unk"])

    # Pre-compiled regex for better performance
    NAME_SANITIZE_REGEX = re.compile(r"[^a-z0-9\-]")

    @staticmethod
    def _get_deployment_command(deployment_type: str, config: Dict[str, Any]) -> list:
        """Generate deployment command based on type and config."""
        if deployment_type == "vllm":
            return [
                "vllm",
                "serve",
                config.get("checkpoint_path", "meta-llama/Llama-3.1-8B-Instruct"),
                f"--tensor-parallel-size={int(config.get('tensor_parallel_size', 1))}",
                f"--pipeline-parallel-size={int(config.get('pipeline_parallel_size', 1))}",
                f"--data-parallel-size={int(config.get('data_parallel_size', 1))}",
                f"--port={int(config.get('port', 8000))}",
                f"--served-model-name={config.get('served_model_name', 'default-model')}",
            ] + (config.get("extra_args", "").split() if config.get("extra_args") else [])
        elif deployment_type == "sglang":
            return [
                "python3",
                "-m",
                "sglang.launch_server",
                f"--model-path={config.get('checkpoint_path', 'meta-llama/Llama-3.1-8B-Instruct')}",
                "--host=0.0.0.0",
                f"--port={int(config.get('port', 8000))}",
                f"--served-model-name={config.get('served_model_name', 'default-model')}",
                f"--tp={int(config.get('tensor_parallel_size', 1))}",
                f"--dp={int(config.get('data_parallel_size', 1))}",
            ] + (config.get("extra_args", "").split() if config.get("extra_args") else [])
        elif deployment_type == "custom":
            return config.get(
                "command", ["/bin/bash", "-c", f"python3 -m http.server {int(config.get('port', 8080))} --bind 0.0.0.0"]
            )
        else:  # nim or unknown
            return []

    def __init__(self, task_type_name: str, connector_name: str):
        super().__init__(task_type_name=task_type_name, metadata_type=LeptonMetadata)
        self.name = connector_name
        # Single client with lazy-loaded API surfaces
        self._client: Optional[APIClient] = None
        self._deployment_api: Optional[DeploymentAPI] = None
        self._log_api: Optional[LogAPI] = None
        self._dashboard_base_url: Optional[str] = None

    @lru_cache(maxsize=128)
    def _sanitize_endpoint_name(self, name: str) -> str:
        """Optimized endpoint name sanitization with caching."""
        sanitized = self.NAME_SANITIZE_REGEX.sub("-", name.lower())

        # Ensure valid start/end characters
        if not sanitized or not sanitized[0].isalpha():
            sanitized = "ep-" + sanitized
        sanitized = sanitized.rstrip("-")
        if not sanitized or not sanitized[-1].isalnum():
            sanitized = sanitized + "x"

        # Efficient truncation with deterministic suffix
        if len(sanitized) > 36:
            return sanitized[:33] + f"{hash(name) % 1000:03d}"
        return sanitized

    def _get_dashboard_base_url(self) -> str:
        """Get dashboard base URL dynamically from workspace origin URL"""
        if self._dashboard_base_url is not None:
            return self._dashboard_base_url

        # Get origin URL from client
        try:
            origin_url = (
                self.client.workspace_origin_url if hasattr(self.client, "workspace_origin_url") else self.ORIGIN_URL
            )
        except Exception:
            origin_url = self.ORIGIN_URL

        # Convert gateway URL to dashboard URL
        if "gateway.dgxc-lepton.nvidia.com" in origin_url:
            self._dashboard_base_url = origin_url.replace(
                "gateway.dgxc-lepton.nvidia.com", "dashboard.dgxc-lepton.nvidia.com"
            )
        elif "gateway.lepton.ai" in origin_url:
            self._dashboard_base_url = origin_url.replace("gateway.lepton.ai", "dashboard.lepton.ai")
        else:
            # Fallback to hardcoded URL if pattern doesn't match
            self._dashboard_base_url = "https://dashboard.dgxc-lepton.nvidia.com"
            log_info(f"Warning: Using fallback dashboard URL for unknown origin: {origin_url}")

        log_info(f"Dynamic dashboard base URL: {self._dashboard_base_url}")
        return self._dashboard_base_url

    def _build_logs_url(self, deployment_name: str, workspace_id: str) -> str:
        """Build dynamic logs URL for deployment"""
        dashboard_base = self._get_dashboard_base_url()
        return f"{dashboard_base}/workspace/{workspace_id}/compute/deployments/detail/{deployment_name}/replicas/list#/deployment/{deployment_name}/logs"

    @property
    def client(self) -> APIClient:
        """Lazy-loaded, cached API client"""
        if self._client is not None:
            return self._client
