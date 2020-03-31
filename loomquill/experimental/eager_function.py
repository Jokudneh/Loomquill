import os
from typing import Optional

from flytekit import current_context
from flytekit.configuration import DataConfig, PlatformConfig, S3Config
from flytekit.core.context_manager import ExecutionState, FlyteContext, FlyteContextManager
from flytekit.loggers import logger
from flytekit.remote import FlyteRemote

FLYTE_SANDBOX_INTERNAL_ENDPOINT = "flyte-sandbox-grpc.flyte:8089"
FLYTE_SANDBOX_MINIO_ENDPOINT = "http://flyte-sandbox-minio.flyte:9000"


def _prepare_remote(
    remote: Optional[FlyteRemote],
    ctx: FlyteContext,
    client_secret_group: Optional[str] = None,
    client_secret_key: Optional[str] = None,
    local_entrypoint: bool = False,
    client_secret_env_var: Optional[str] = None,
) -> Optional[FlyteRemote]:
    """Prepare FlyteRemote object for accessing Flyte cluster in a task running on the same cluster."""

    is_local_execution_mode = ctx.execution_state.mode in {
        ExecutionState.Mode.LOCAL_TASK_EXECUTION,
        ExecutionState.Mode.LOCAL_WORKFLOW_EXECUTION,
    }

    if remote is not None and local_entrypoint and is_local_execution_mode:
        # when running eager workflows as a local entrypoint, we don't have to modify the remote object
