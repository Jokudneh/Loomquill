import re
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

from flyteidl.core import security_pb2 as _sec

from flytekit.models import common as _common


@dataclass
class Secret(_common.FlyteIdlEntity):
    """
    See :std:ref:`cookbook:secrets` for usage examples.

    Args:
        group is the Name of the secret. For example in kubernetes secrets is the name of the secret
        key is optional and can be an individual secret identifier within the secret For k8s this is required
        version is the version of the secret. This is an optional field
        mount_requirement provides a hint to the system as to how the secret should be injected
        env_var is optional. Custom environment name to set the value of the secret.
            If mount_requirement is ENV_VAR, then the value is the secret itself.
            If mount_requirement is FILE, then the value is the path to the secret file.
    """

    class MountType(Enum):
        ANY = _sec.Secret.MountType.ANY
        """
        Use this if the secret can be injected as either an environment variable / file and this should be left for the
        platform to decide. This is the most flexible option
        """
        ENV_VAR = _sec.Secret.MountType.ENV_VAR
        """
        Use this if the secret can be injected as an environment variable. Usually works for symmetric keys, passwords etc
        """
        FILE = _sec.Secret.MountType.FILE
        """
        Use this for Secrets that cannot be injected into env-var or need to be available as a file
        Caution: May not be supported in all environments
        """

    group: Optional[str] = None
    key: Optional[str] = None
    group_version: Optional[str] = None
    mount_requirement: MountType = MountType.ANY
    env_var: Optional[str] = None

    def __post_init__(self):
        from flytekit.configuration.plugin import get_plugin
        from flytekit.core.context_manager import FlyteContextManager

        # Only check for the groups during registration.
        execution = FlyteContextManager.current_context().execution_state
        in_registration_context = execution.mode is None
        if in_registration_context and get_plugin().secret_requires_group() and self.group is None:
