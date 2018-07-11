import copy
import datetime
import inspect
import os
import shutil
import tempfile
import time
import typing
from abc import ABC, abstractmethod
from functools import wraps
from hashlib import sha224 as _sha224
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, cast

from flyteidl.core import tasks_pb2 as _core_task

from flytekit.configuration import SerializationSettings
from flytekit.core.pod_template import PodTemplate
from flytekit.core.resources import ResourceSpec, _check_resource_is_singular
from flytekit.loggers import logger

if TYPE_CHECKING:
    from flytekit.models import task as task_models


def _dnsify(value: str) -> str:
    """
    Converts value into a DNS-compliant (RFC1035/RFC1123 DNS_LABEL). The resulting string must only consist of
    alphanumeric (lower-case a-z, and 0-9) and not exceed 63 characters. It's permitted to have '-' character as long
    as it's not in the first or last positions.

    :param Text value:
    :rtype: Text
    """
    res = ""
    MAX = 63
    HASH_LEN = 10
    if len(value) >= MAX:
        h = _sha224(value.encode("utf-8")).hexdigest()[:HASH_LEN]
        value = "{}-{}".format(h, value[-(MAX - HASH_LEN - 1) :])
    for ch in value:
        if ch == "_" or ch == "-" or ch == ".":
            # Convert '_' to '-' unless it's the first character, in which case we drop it.
            if res != "" and len(res) < 62:
                res += "-"
        elif not ch.isalnum():
            # Trim non-alphanumeric letters.
            pass
        elif ch.islower() or ch.isdigit():
            # Character is already compliant, just append it.
            res += ch
        else:
            # Character is upper-case. Add a '-' before it for better readability.
            if res != "" and res[-1] != "-" and len(res) < 62:
                res += "-"
            res += ch.lower()

    if len(res) > 0 and res[-1] == "-":
        res = res[: len(res) - 1]

    return res


def _get_container_definition(
    image: str,
    resource_spec: ResourceSpec,
    command: List[str],
    args: Optional[List[str]] = None,
    data_loading_config: Optional["task_models.DataLoadingConfig"] = None,
    environment: Optional[Dict[str, str]] = None,
) -> "task_models.Container":
    limits = _check_resource_is_singular(resource_spec.limits)
    requests = _check_resource_is_singular(resource_spec.requests)

    ephemeral_storage_limit = limits.ephemeral_storage
    ephemeral_storage_request = requests.ephemeral_storage
    cpu_limit = limits.cpu
    cpu_request = requests.cpu
    gpu_limit = limits.gpu
    gpu_request = requests.gpu
    memory_limit = limits.mem
    memory_request = requests.mem

    from flytekit.models import task as task_models

    # TODO: Use convert_resources_to_resource_model instead of manually fixing the resources.
    requests = []
    if ephemeral_storage_request:
        requests.append(
            task_models.Resources.ResourceEntry(
                task_models.Resources.ResourceName.EPHEMERAL_STORAGE,
                ephemeral_storage_request,
            )
        )
    if cpu_request:
        requests.append(task_models.Resources.ResourceEntry(task_models.Resources.ResourceName.CPU, cpu_request))
    if gpu_request:
        requests.append(task_models.Resources.ResourceEntry(task_models.Resources.ResourceName.GPU, gpu_request))
    if memory_request:
        requests.append(task_models.Resources.ResourceEntry(task_models.Resources.ResourceName.MEMORY, memory_request))

    limits = []
