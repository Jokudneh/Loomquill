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
