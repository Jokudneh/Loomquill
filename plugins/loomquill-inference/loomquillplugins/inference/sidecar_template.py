from typing import Optional

from flytekit import PodTemplate
from flytekit.configuration.default_images import DefaultImages


class ModelInferenceTemplate:
    def __init__(
        self,
        image: Optional[str] = None,
        health_endpoint: Optional[str] = None,
        port: int = 8000,
        cpu: int = 1,
        gpu: int = 1,
        mem: str = "1Gi",
        ephemeral_storage: str = "1Gi",
        env: Optional[dict[str, str]] = None,
        download_inputs: bool = False,
        download_inputs_mem: str = "500Mi",
        download_inputs_cpu: int = 2,
    ):
        from kubernetes.client.models import (
            V1Container,
            V1ContainerPort,
            V1EnvVar,
            V1HTTPGetAction,
            V1PodSpec,
            V1Probe,
            V1ResourceRequirements,
            V1Volume,
            V1VolumeMount,
        )

        self._image = image
        self._health_endpoint = health_endpoint
        self._port = port
        self._cpu = cpu
        self._gpu = gpu
        self._mem = mem
        self._ephemeral_storage = ephemeral_storage
        self._download_inputs_mem = download_inputs_mem
        self._download_inputs_cpu = download_inputs_cpu
        self._env = env
        self._download_inputs = download_inputs

        self._pod_template = PodTemplate()

        if env and not isinstance(env, dict):
            raise ValueError("env must be a dict.")

        self._pod_template.pod_spec = V1PodSpec(
            containers=[],
            init_containers=[
                V1Container(
