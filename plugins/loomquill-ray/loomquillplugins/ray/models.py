import typing

from flyteidl.core import literals_pb2 as _literals_pb2
from flyteidl.plugins import ray_pb2 as _ray_pb2

from flytekit.models import common as _common
from flytekit.models import task as _task_models
from flytekit.models.task import K8sPod


class WorkerGroupSpec(_common.FlyteIdlEntity):
    def __init__(
        self,
        group_name: str,
        replicas: int,
        min_replicas: typing.Optional[int] = None,
        max_replicas: typing.Optional[int] = None,
        ray_start_params: typing.Optional[typing.Dict[str, str]] = None,
        k8s_pod: typing.Optional[K8sPod] = None,
    ):
        self._group_name = group_name
        self._replicas = replicas
        self._max_replicas = max(replicas, max_replicas) if max_replicas is not None else replicas
        self._min_replicas = min(replicas, min_replicas) if min_replicas is not None else replicas
        self._ray_start_params = ray_start_params
        self._k8s_pod = k8s_pod

    @property
    def group_name(self):
        """
        Group name of the current worker group.
        :rtype: str
        """
        return self._group_name

    @property
    def replicas(self):
        """
        Desired replicas of the worker group.
        :rtype: int
        """
        return self._replicas

    @property
    def min_replicas(self):
        """
        Min replicas of the worker group.
        :rtype: int
        """
        return self._min_replicas

    @property
    def max_replicas(self):
        """
        Max replicas of the worker group.
        :rtype: int
        """
        return self._max_replicas

    @property
    def ray_start_params(self):
        """
        The ray start params of worker node group.
        :rtype: typing.Dict[str, str]
        """
        return self._ray_start_params

    @property
    def k8s_pod(self):
        """
        Additional pod specs for the worker node pods.
        :rtype: K8sPod
        """
        return self._k8s_pod

    def to_flyte_idl(self):
        """
        :rtype: flyteidl.plugins._ray_pb2.WorkerGroupSpec
        """
        return _ray_pb2.WorkerGroupSpec(
            group_name=self.group_name,
            replicas=self.replicas,
            min_replicas=self.min_replicas,
            max_replicas=self.max_replicas,
            ray_start_params=self.ray_start_params,
            k8s_pod=self.k8s_pod.to_flyte_idl() if self.k8s_pod else None,
        )

    @classmethod
    def from_flyte_idl(cls, proto):
        """
        :param flyteidl.plugins._ray_pb2.WorkerGroupSpec proto:
        :rtype: WorkerGroupSpec
        """
        return cls(
            group_name=proto.group_name,
            replicas=proto.replicas,
            min_replicas=proto.min_replicas,
            max_replicas=proto.max_replicas,
            ray_start_params=proto.ray_start_params,
            k8s_pod=K8sPod.from_flyte_idl(proto.k8s_pod) if proto.HasField("k8s_pod") else None,
        )


class HeadGroupSpec(_common.FlyteIdlEntity):
    def __init__(
        self,
        ray_start_params: typing.Optional[typing.Dict[str, str]] = None,
        k8s_pod: typing.Optional[K8sPod] = None,
    ):
        self._ray_start_params = ray_start_params
