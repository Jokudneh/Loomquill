import json as _json
import typing

from flyteidl.admin import agent_pb2 as _admin_agent
from flyteidl.admin import task_pb2 as _admin_task
from flyteidl.core import compiler_pb2 as _compiler
from flyteidl.core import literals_pb2 as _literals_pb2
from flyteidl.core import tasks_pb2 as _core_task
from google.protobuf import json_format as _json_format
from google.protobuf import struct_pb2 as _struct
from google.protobuf.wrappers_pb2 import BoolValue

from flytekit.models import common as _common
from flytekit.models import interface as _interface
from flytekit.models import literals as _literals
from flytekit.models import security as _sec
from flytekit.models.core import identifier as _identifier
from flytekit.models.documentation import Documentation

if typing.TYPE_CHECKING:
    from flytekit import PodTemplate


class Resources(_common.FlyteIdlEntity):
    class ResourceName(object):
        UNKNOWN = _core_task.Resources.UNKNOWN
        CPU = _core_task.Resources.CPU
        GPU = _core_task.Resources.GPU
        MEMORY = _core_task.Resources.MEMORY
        EPHEMERAL_STORAGE = _core_task.Resources.EPHEMERAL_STORAGE

    class ResourceEntry(_common.FlyteIdlEntity):
        def __init__(self, name, value):
            """
            :param int name: enum value from ResourceName
            :param Text value: a textual value describing the resource need.  Must be a valid k8s quantity.
            """
            self._name = name
            self._value = value

        @property
        def name(self):
            """
            enum value from ResourceName
            :rtype: int
            """
            return self._name

        @property
        def value(self):
            """
            A textual value describing the resource need.  Must be a valid k8s quantity.
            :rtype: Text
            """
            return self._value

        def to_flyte_idl(self):
            """
            :rtype: flyteidl.core.tasks_pb2.ResourceEntry
            """
            return _core_task.Resources.ResourceEntry(name=self.name, value=self.value)

        @classmethod
        def from_flyte_idl(cls, pb2_object):
            """
            :param flyteidl.core.tasks_pb2.Resources.ResourceEntry pb2_object:
            :rtype: Resources.ResourceEntry
            """
            return cls(name=pb2_object.name, value=pb2_object.value)

    def __init__(self, requests, limits):
        """
        :param list[Resources.ResourceEntry] requests: The desired resources for execution.  This is given on a best
            effort basis.
        :param list[Resources.ResourceEntry] limits: These are the limits required.  These are guaranteed to be
            satisfied.
        """
        self._requests = requests
        self._limits = limits

    @property
    def requests(self):
        """
        The desired resources for execution.  This is given on a best effort basis.
        :rtype: list[Resources.ResourceEntry]
        """
        return self._requests

    @property
    def limits(self):
        """
        These are the limits required.  These are guaranteed to be satisfied.
        :rtype: list[Resources.ResourceEntry]
        """
        return self._limits

    def to_flyte_idl(self):
        """
        :rtype: flyteidl.core.tasks_pb2.Resources
        """
        return _core_task.Resources(
            requests=[r.to_flyte_idl() for r in self.requests],
            limits=[r.to_flyte_idl() for r in self.limits],
        )

    @classmethod
    def from_flyte_idl(cls, pb2_object):
        """
        :param flyteidl.core.tasks_pb2.Resources.ResourceEntry pb2_object:
        :rtype: Resources
        """
        return cls(
            requests=[Resources.ResourceEntry.from_flyte_idl(r) for r in pb2_object.requests],
            limits=[Resources.ResourceEntry.from_flyte_idl(l) for l in pb2_object.limits],
        )


class RuntimeMetadata(_common.FlyteIdlEntity):
    class RuntimeType(object):
        OTHER = 0
        FLYTE_SDK = 1

    def __init__(self, type, version, flavor):
        """
        :param int type: Enum type from RuntimeMetadata.RuntimeType
        :param Text version: Version string for SDK version.  Can be used for metrics or managing breaking changes in
            Admin or Propeller
        :param Text flavor: Optional extra information about runtime environment (e.g. Python, GoLang, etc.)
        """
        self._type = type
        self._version = version
        self._flavor = flavor

    @property
    def type(self):
        """
        Enum type from RuntimeMetadata.RuntimeType
        :rtype: int
        """
        return self._type

    @property
    def version(self):
        """
        Version string for SDK version.  Can be used for metrics or managing breaking changes in Admin or Propeller
        :rtype: Text
        """
        return self._version

    @property
    def flavor(self):
        """
        Optional extra information about runtime environment (e.g. Python, GoLang, etc.)
        :rtype: Text
        """
        return self._flavor

    def to_flyte_idl(self):
        """
        :rtype: flyteidl.core.tasks_pb2.RuntimeMetadata
        """
        return _core_task.RuntimeMetadata(type=self.type, version=self.version, flavor=self.flavor)

    @classmethod
    def from_flyte_idl(cls, pb2_object):
        """
        :param flyteidl.core.tasks_pb2.RuntimeMetadata pb2_object:
        :rtype: RuntimeMetadata
        """
        return cls(type=pb2_object.type, version=pb2_object.version, flavor=pb2_object.flavor)


class TaskMetadata(_common.FlyteIdlEntity):
    def __init__(
        self,
        discoverable,
        runtime,
        timeout,
        retries,
        interruptible,
        discovery_version,
        deprecated_error_message,
        cache_serializable,
        pod_template_name,
        cache_ignore_input_vars,
        is_eager: bool = False,
        generates_deck: bool = False,
        k8s_object_metadata: typing.Optional["K8sObjectMetadata"] = None,
    ):
        """
        Information needed at runtime to determine behavior such as whether or not outputs are discoverable, timeouts,
        and retries.

        :param bool discoverable: Whether or not the outputs of this task should be cached for discovery.
        :param RuntimeMetadata runtime: Metadata describing the runtime environment for this task.
        :param datetime.timedelta timeout: The amount of time to wait before timing out.  This includes queuing and
            scheduler latency.
        :param bool interruptible: Whether or not the task is interruptible.
        :param flytekit.models.literals.RetryStrategy retries: Retry strategy for this task.  0 retries means only
            try once.
        :param Text discovery_version: This is the version used to create a logical version for data in the cache.
            This is only used when `discoverable` is true.  Data is considered discoverable if: the inputs to a given
            task are the same and the discovery_version is also the same.
        :param Text deprecated: This string can be used to mark the task as deprecated.  Consumers of the task will
            receive deprecation warnings.
        :param bool cache_serializable: Whether or not caching operations are executed in serial. This means only a
            single instance over identical inputs is executed, other concurrent executions wait for the cached results.
        :param bool generates_deck: Whether the task will generate a Deck URI.
        :param pod_template_name: The name of the existing PodTemplate resource which will be used in this task.
        :param cache_ignore_input_vars: Input variables that should not be included when calculating hash for cache.
        :param is_eager:
        :param metadata: Kubernetes metadata for the task.
        """
        self._discoverable = discoverable
        self._runtime = runtime
        self._timeout = timeout
        self._interruptible = interruptible
        self._retries = retries
        self._discovery_version = discovery_version
        self._deprecated_error_message = deprecated_error_message
        self._cache_serializable = cache_serializable
        self._pod_template_name = pod_template_name
        self._cache_ignore_input_vars = cache_ignore_input_vars
        self._is_eager = is_eager
        self._generates_deck = generates_deck
        self._k8s_object_metadata = k8s_object_metadata

    @property
    def is_eager(self):
        return self._is_eager

    @property
    def discoverable(self):
        """
        Whether or not the outputs of this task should be cached for discovery.
        :rtype: bool
        """
        return self._discoverable

    @property
    def runtime(self):
        """
        Metadata describing the runtime environment for this task.
        :rtype: RuntimeMetadata
        """
        return self._runtime

    @property
    def retries(self):
        """
        Retry strategy for this task.  0 retries means only try once.
        :rtype: flytekit.models.literals.RetryStrategy
        """
        return self._retries

    @property
    def timeout(self):
        """
        The amount of time to wait before timing out.  This includes queuing and scheduler latency.
        :rtype: datetime.timedelta
        """
        return self._timeout

    @property
    def interruptible(self):
        """
        Whether or not the task is interruptible.
        :rtype: bool
        """
        return self._interruptible

    @property
    def discovery_version(self):
        """
        This is the version used to create a logical version for data in the cache.
        This is only used when `discoverable` is true.  Data is considered discoverable if: the inputs to a given
        task are the same and the discovery_version is also the same.
        :rtype: Text
        """
        return self._discovery_version

    @property
    def deprecated_error_message(self):
        """
        This string can be used to mark the task as deprecated.  Consumers of the task will receive deprecation
        warnings.
        :rtype: Text
        """
        return self._deprecated_error_message

    @property
    def cache_serializable(self):
        """
        Whether or not caching operations are executed in serial. This means only a single instance over identical
        inputs is executed, other concurrent executions wait for the cached results.
        :rtype: bool
        """
        return self._cache_serializable

    @property
    def pod_template_name(self):
        """
        The name of the existing PodTemplate resource which will be used in this task.
        :rtype: Text
        """
        return self._pod_template_name

    @property
    def generates_deck(self) -> bool:
        """
        Whether the task will generate a Deck.
        :rtype: bool
        """
        return self._generates_deck

    @property
    def cache_ignore_input_vars(self):
        """
        Input variables that should not be included when calculating hash for cache.
        :rtype: tuple[Text]
        """
        return self._cache_ignore_input_vars

    @property
    def k8s_object_metadata(self) -> typing.Optional["K8sObjectMetadata"]:
        """
        Kubernetes metadata for the task.
