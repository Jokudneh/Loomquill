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
        except kubernetes.config.ConfigException as e:
            logger.error(f"Failed to load kubernetes config: {e}")
            raise
        self.apps_v1_api = client.AppsV1Api()
        self.core_v1_api = client.CoreV1Api()
        self.custom_api = client.CustomObjectsApi()
        self.namespace = namespace

    async def poke(self, release_name: str, cleanup_data_service: bool, cluster: str) -> bool:
        """poke will delete the graph engine resources based on the user's configuration
        1. This has to be done in the control plane by design. We don't expect any users's running pod to be authn/z to manage resources
        2. This can not be done in the async connector because the delete callback is only invoked on abortion operation or failure phase.
