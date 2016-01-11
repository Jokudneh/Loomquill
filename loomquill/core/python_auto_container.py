from __future__ import annotations

import importlib
import re
from abc import ABC
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, TypeVar, Union
from typing import Literal as L

from flyteidl.core import tasks_pb2

from flytekit.configuration import ImageConfig, SerializationSettings
from flytekit.constants import CopyFileDetection
from flytekit.core.base_task import PythonTask, TaskMetadata, TaskResolverMixin
from flytekit.core.constants import RUNTIME_PACKAGES_ENV_NAME
from flytekit.core.context_manager import FlyteContextManager
from flytekit.core.pod_template import PodTemplate
from flytekit.core.resources import Resources, ResourceSpec, construct_extended_resources
from flytekit.core.tracked_abc import FlyteTrackedABC
from flytekit.core.tracker import TrackedInstance, extract_task_module
from flytekit.core.utils import _get_container_definition, _serialize_pod_spec, timeit
from flytekit.extras.accelerators import BaseAccelerator
from flytekit.image_spec.image_spec import ImageBuildEngine, ImageSpec
from flytekit.loggers import logger
from flytekit.models import task as _task_model
from flytekit.models.security import Secret, SecurityContext

T = TypeVar("T")
_PRIMARY_CONTAINER_NAME_FIELD = "primary_container_name"
PICKLE_FILE_PATH = "pkl.gz"


class PythonAutoContainerTask(PythonTask[T], ABC, metaclass=FlyteTrackedABC):
    """
    A Python AutoContainer task should be used as the base for all extensions that want the user's code to be in the
    container and the container information to be automatically captured.
    This base will auto configure the image and image version to be used for all its derivatives.

    If you are looking to extend, you might prefer to use ``PythonFunctionTask`` or ``PythonInstanceTask``
    """

    def __init__(
        self,
        name: str,
        task_config: T,
        task_type="python-task",
        container_image: Optional[Union[str, ImageSpec]] = None,
        requests: Optional[Resources] = None,
        limits: Optional[Resources] = None,
        environment: Optional[Dict[str, str]] = None,
        task_resolver: Optional[TaskResolverMixin] = None,
        secret_requests: Optional[List[Secret]] = None,
        pod_template: Optional[PodTemplate] = None,
        pod_template_name: Optional[str] = None,
        accelerator: Optional[BaseAccelerator] = None,
        shared_memory: Optional[Union[L[True], str]] = None,
        resources: Optional[Resources] = None,
        **kwargs,
    ):
        """
        :param name: unique name for the task, usually the function's module and name.
        :param task_config: Configuration object for Task. Should be a unique type for that specific Task.
        :param task_type: String task type to be associated with this Task
        :param container_image: String FQN for the image.
        :param requests: custom resource request settings.
        :param limits: custom resource limit settings.
        :param environment: Environment variables you want the task to have when run.
        :param task_resolver: Custom resolver - will pick up the default resolver if empty, or the resolver set
          in the compilation context if one is set.
        :param List[Secret] secret_requests: Secrets that are requested by this container execution. These secrets will
           be mounted based on the configuration in the Secret and available through
           the SecretManager using the name of the secret as the group
           Ideally the secret keys should also be semi-descriptive.
           The key values will be available from runtime, if the backend is configured
           to provide secrets and if secrets are available in the configured secrets store.
           Possible options for secret stores are

           - [`Vault`](https://www.vaultproject.io/)
           - [`Confidant`](https://lyft.github.io/confidant)
           - [`Kube secrets`](https://kubernetes.io/docs/concepts/configuration/secret)
           - [`AWS Parameter store`](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html)
        :param pod_template: Custom PodTemplate for this task.
        :param pod_template_name: The name of the existing PodTemplate resource which will be used in this task.
        :param accelerator: The accelerator to use for this task.
        :param shared_memory: If True, then shared memory will be attached to the container where the size is equal
            to the allocated memory. If str, then the shared memory is set to that size.
        :param resources: Specify both the request and the limit. When the value is set to a tuple or list, the
            first value is the request and the second value is the limit. If the value is a single value, then both the
            requests and limit is set to that value. For example, the `Resource(cpu=("1", "2"), mem="1Gi")` will set
            the cpu request to 1, cpu limit to 2, and mem request to 1Gi.
        """
        sec_ctx = None
        if secret_requests:
            for s in secret_requests:
                if not isinstance(s, Secret):
                    raise AssertionError(f"Secret {s} should be of type flytekit.Secret, received {type(s)}")
            sec_ctx = SecurityContext(secrets=secret_requests)

        # pod_template_name overwrites the metadata.pod_template_name
        kwargs["metadata"] = kwargs["metadata"] if "metadata" in kwargs else TaskMetadata()
        kwargs["metadata"].pod_template_name = pod_template_name

        if kwargs.get("labels") is not None:
            kwargs["metadata"].labels = kwargs["labels"]
        if kwargs.get("annotations") is not None:
            kwargs["metadata"].annotations = kwargs["annotations"]

        self._container_image = container_image
        # TODO(katrogan): Implement resource overrides

        if resources is not None:
            if limits is not None or requests is not None:
                msg = "`resource` can not be used together with the `limits` or `requests`. Please only set `resource`."
                raise ValueError(msg)
            self._resources = ResourceSpec.from_multiple_resource(resources)
        else:
            self._resources = ResourceSpec(
                requests=Resources() if requests is None else requests,
                limits=Resources() if limits is None else limits,
            )

        # The serialization of the other tasks (Task -> protobuf), as well as the initialization of the current task, may occur simultaneously.
        # We should make sure super().__init__ is being called after setting _container_image because PythonAutoContainerTask
        # is added to the FlyteEntities in super().__init__, and the translator will iterate over
        # FlyteEntities and call entity.container_image().
        # Therefore, we need to ensure the _container_image attribute is set
        # before appending the task to FlyteEntities.
        # https://github.com/flyteorg/flytekit/blob/876877abd8d6f4f54dec2738a0ca07a12e9115b1/flytekit/tools/translator.py#L181

        super().__init__(
            task_type=task_type,
            name=name,
            task_config=task_config,
            security_ctx=sec_ctx,
            environment=environment,
            **kwargs,
        )

        compilation_state = FlyteContextManager.current_context().compilation_state
        if compilation_state and compilation_state.task_resolver:
            if task_resolver:
                logger.info(
                    f"Not using the passed in task resolver {task_resolver} because one found in compilation context"
                )
            self._task_resolver = compilation_state.task_resolver
            if self._task_resolver.task_name(self) is not None:
