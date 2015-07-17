from flytekitplugins.k8sdataservice.k8s.kube_config import KubeConfig
from kubernetes import client
from kubernetes.client.rest import ApiException

from flytekit import logger
from flytekit.sensor.base_sensor import BaseSensor

TRAININGJOB_API_GROUP = "kubeflow.org"
VERSION = "v1"


class CleanupSensor(BaseSensor):
    def __init__(self, name: str, namespace: str = "flyte", **kwargs):
        """
        Initialize the CleanupSensor class with relevant configurations for monitoring and managing the k8s data service.
        """
        super().__init__(name=name, task_type="sensor", **kwargs)
        self.k8s_config = KubeConfig()
        try:
            self.k8s_config.load_kube_config()
