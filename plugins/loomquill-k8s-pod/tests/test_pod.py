import json
from collections import OrderedDict
from typing import List
from unittest.mock import MagicMock

import pytest
from flytekitplugins.pod.task import Pod, PodFunctionTask
from kubernetes.client import ApiClient
from kubernetes.client.models import V1Container, V1EnvVar, V1PodSpec, V1ResourceRequirements, V1VolumeMount

from flytekit import Resources, TaskMetadata, dynamic, map_task, task
from flytekit.configuration import FastSerializationSettings, Image, ImageConfig, SerializationSettings
from flytekit.core import context_manager
from flytekit.core.type_engine import TypeEngine
from flytekit.exceptions import user
from flytekit.extend import ExecutionState
from flytekit.tools.translator import get_serializable


def get_pod_spec(environment=[]):
    a_container = V1Container(
        name="a container",
        env=environment,
    )
    a_container.command = ["fee", "fi", "fo", "fum"]
    a_container.volume_mounts = [
        V1VolumeMount(
            name="volume mount",
            mount_path="some/where",
        )
    ]

    pod_spec = V1PodSpec(restart_policy="OnFailure", containers=[a_container, V1Container(name="another container")])
    return pod_spec


@pytest.mark.parametrize(
    "task_environment, podspec_env_vars, expected_environment",
    [
        ({"FOO": "bar"}, [], [V1EnvVar(name="FOO", value="bar")]),
        (
            {"FOO": "bar"},
            [V1EnvVar(name="AN_ENV_VAR", value="42")],
            [V1EnvVar(name="FOO", value="bar"), V1EnvVar(name="AN_ENV_VAR", value="42")],
        ),
        # We do not provide any validation for the duplication of env vars, neither does k8s.
        (
            {"FOO": "bar"},
            [V1EnvVar(name="FOO", value="another-bar")],
            [V1EnvVar(name="FOO", value="bar"), V1EnvVar(name="FOO", value="another-bar")],
        ),
    ],
)
def test_pod_task_deserialization(task_environment, podspec_env_vars, expected_environment):
    pod = Pod(pod_spec=get_pod_spec(podspec_env_vars), primary_container_name="a container")

    @task(task_config=pod, requests=Resources(cpu="10"), limits=Resources(gpu="2"), environment=task_environment)
    def simple_pod_task(i: int):
        pass

    assert isinstance(simple_pod_task, PodFunctionTask)
    assert simple_pod_task.task_config == pod

    default_img = Image(name="default", fqn="test", tag="tag")

    target = simple_pod_task.get_k8s_pod(
        SerializationSettings(
            project="project",
            domain="domain",
            version="version",
            env={"FOO": "baz"},
            image_config=ImageConfig(default_image=default_img, images=[default_img]),
        )
    )

    # Test that custom is correctly serialized by deserializing it with the python API client
    response = MagicMock()
    response.data = json.dumps(target.pod_spec)
    deserialized_pod_spec = ApiClient().deserialize(response, V1PodSpec)

    assert deserialized_pod_spec.restart_policy == "OnFailure"
    assert len(deserialized_pod_spec.containers) == 2
    primary_container = deserialized_pod_spec.containers[0]
