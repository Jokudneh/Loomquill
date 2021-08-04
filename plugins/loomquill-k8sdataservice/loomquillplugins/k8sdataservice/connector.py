from dataclasses import dataclass
from typing import Optional

from flyteidl.core.execution_pb2 import TaskExecution
from flytekitplugins.k8sdataservice.k8s.manager import K8sManager
from flytekitplugins.k8sdataservice.task import DataServiceConfig

from flytekit import logger
from flytekit.extend.backend.base_connector import AsyncConnectorBase, ConnectorRegistry, Resource, ResourceMeta
from flytekit.models.literals import LiteralMap
from flytekit.models.task import TaskTemplate


@dataclass
class DataServiceMetadata(ResourceMeta):
    dataservice_config: DataServiceConfig
    name: str


class DataServiceConnector(AsyncConnectorBase):
    name = "K8s DataService Async Connector"

    def __init__(self):
        self.k8s_manager = K8sManager()
        super().__init__(task_type_name="dataservicetask", metadata_type=DataServiceMetadata)
        self.config = None

    def create(
        self, task_template: TaskTemplate, output_prefix: str, inputs: Optional[LiteralMap] = None, **kwargs
    ) -> DataServiceMetadata:
        graph_engine_config = task_template.custom
        self.k8s_manager.set_configs(graph_engine_config)
        logger.info(f"Loaded connector config file {self.config}")
