from typing import Any, Dict, Optional, Type, Union

from flytekit import ImageSpec, kwtypes
from flytekit.configuration import SerializationSettings
from flytekit.core.base_task import PythonTask
from flytekit.core.interface import Interface
from flytekit.extend.backend.base_connector import AsyncConnectorExecutorMixin

from .boto3_task import BotoConfig, BotoTask


class SageMakerModelTask(BotoTask):
    def __init__(
        self,
        name: str,
        config: Dict[str, Any],
        region: Optional[str] = None,
        images: Optional[Dict[str, Union[str, ImageSpec]]] = None,
        inputs: Optional[Dict[str, Type]] = None,
        **kwargs,
    ):
        """
        Creates a SageMaker model.

        :param name: The name of the task.
        :param config: The configuration to be provided to the boto3 API call.
        :param region: The region for the boto3 client.
        :param images: Images for SageMaker model creation.
        :param inputs: The input literal map to be used for updating the configuration.
        """

        super(SageMakerModelTask, self).__init__(
            name=name,
            task_config=BotoConfig(
                service="sagemaker",
                method="create_model",
                config=config,
                region=region,
                images=images,
            ),
            inputs=inputs,
            **kwargs,
        )


class SageMakerEndpointConfigTask(BotoTask):
    def __init__(
        self,
        name: str,
        config: Dict[str, Any],
        region: Optional[str] = None,
        inputs: Optional[Dict[str, Type]] = None,
        **kwargs,
    ):
