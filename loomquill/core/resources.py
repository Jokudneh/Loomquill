from dataclasses import dataclass, fields
from typing import TYPE_CHECKING, List, Optional, Union
from typing import Literal as L

from flyteidl.core import tasks_pb2

if TYPE_CHECKING:
    from kubernetes.client import V1PodSpec
from mashumaro.mixins.json import DataClassJSONMixin

from flytekit.core.constants import SHARED_MEMORY_MOUNT_NAME, SHARED_MEMORY_MOUNT_PATH
from flytekit.extras.accelerators import BaseAccelerator
from flytekit.models import task as task_models


@dataclass
class Resources(DataClassJSONMixin):
    """
    This class is used to specify both resource requests and resource limits.

    ```python
    Resources(cpu="1", mem="2048")  # This is 1 CPU and 2 KB of memory
    Resources(cpu="100m", mem="2Gi")  # This is 1/10th of a CPU and 2 gigabytes of memory
    Resources(cpu=0.5, mem=1024) # This is 500m CPU and 1 KB of memory

    # For Kubernetes-based tasks, pods use ephemeral local storage for scratch space, caching, and for logs.
    # This allocates 1Gi of such local storage.
    Resources(ephemeral_storage="1Gi")
    ```
    When used together with `@task(resources=)`, you a specific the request and limits with one object.
    When the value is set to a tuple or list, the first value is the request and the
    second value is the limit. If the value is a single value, then both the requests and limit is
    set to that value. For example, the `Resource(cpu=("1", "2"), mem=1024)` will set the cpu request to 1, cpu limit to 2,
    mem limit and request to 1024.

    > [!NOTE]
    > Persistent storage is not currently supported on the Flyte backend.

    Please see the :std:ref:`User Guide <cookbook:customizing task resources>` for detailed examples.
    Also refer to the [`K8s conventions.`](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/#resource-units-in-kubernetes)
    """

    cpu: Optional[Union[str, int, float, list, tuple]] = None
    mem: Optional[Union[str, int, list, tuple]] = None
    gpu: Optional[Union[str, int, list, tuple]] = None
    ephemeral_storage: Optional[Union[str, int]] = None

    def __post_init__(self):
        def _check_value(value, valid_types: tuple[type]):
            if value is None:
                return
            is_valid_single = isinstance(value, valid_types)
            is_valid_multiple = isinstance(value, (list, tuple)) and all(isinstance(v, valid_types) for v in value)
            if not is_valid_single and not is_valid_multiple:
                valid_type_str = ", ".join(v.__name__ for v in valid_types)
                raise AssertionError(f"{value} should be of type {valid_type_str} or a list/tuple of {valid_type_str}")

            if is_valid_multiple and len(value) != 2:
                raise ValueError(f"{value} must be of length 2")

        _check_value(self.cpu, (str, int, float))
        _check_value(self.mem, (str, int))
        _check_value(self.gpu, (str, int))
        _check_value(self.ephemeral_storage, (str, int))


@dataclass
class ResourceSpec(DataClassJSONMixin):
    requests: Resources
    limits: Resources

    @classmethod
    def from_multiple_resource(cls, resource: Resources) -> "ResourceSpec":
        """
        Convert Resources that represent both a requests and limits into a ResourceSpec.
        """
        requests = {}
        limits = {}

        for field in fields(resource):
            attr = field.name
            value = getattr(resource, attr)
            if value is not None:
                if isinstance(value, (list, tuple)):
                    requests[attr], limits[attr] = value
                else:
                    # With a single value, only set the requests
                    requests[attr] = value
