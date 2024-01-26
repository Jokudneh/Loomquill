import uuid

from flytekitplugins.k8sdataservice.k8s.kube_config import KubeConfig
from kubernetes import client
from kubernetes.client.rest import ApiException
from utils.resources import cleanup_resources, convert_flyte_to_k8s_fields

from flytekit import logger

APPNAME = "service-name"
DEFAULT_RESOURCES = client.V1ResourceRequirements(
    requests={"cpu": "2", "memory": "10G"}, limits={"cpu": "6", "memory": "16G"}
)


class K8sManager:
    def __init__(self):
        self.config = KubeConfig()
        self.config.load_kube_config()
        self.apps_v1_api = client.AppsV1Api()
        self.core_v1_api = client.CoreV1Api()

    def set_configs(self, data_service_config):
        self.data_service_config = data_service_config
        self.labels = {}
        self.namespace = "flyte"
        self.name = None
        self.name = data_service_config.get("Name", None)
        if self.name is None:
            self.name = f"k8s-dataservice-{uuid.uuid4().hex[:8]}"

    def create_data_service(self) -> str:
        svc_name = self.create_service()
        logger.info(f"Created service: {svc_name}")
        stateful_set_obj = self.create_stateful_set_object()
        name = self.create_stateful_set(stateful_set_obj)
        return name

    def create_stateful_set(self, stateful_set_object) -> str:
        api_response = None
        try:
            api_response = self.apps_v1_api.create_namespaced_stateful_set(
                namespace=self.namespace, body=stateful_set_object
            )
            logger.info(f"Created statefulset in K8s API server: {api_response}")
        except ApiException as e:
            logger.error(f"Exception when calling AppsV1Api->create_namespaced_stateful_set: {e}\n")
            raise
        return api_response.metadata.name

    def create_stateful_set_object(self):
        container = self._create_container()
        template = self._create_pod_template(container)
        spec = self._create_stateful_set_spec(template)
        return client.V1StatefulSet(
            api_version="apps/v1",
