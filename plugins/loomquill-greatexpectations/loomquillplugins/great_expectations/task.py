import datetime
import os
import shutil
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Type, Union

from dataclasses_json import DataClassJsonMixin

from flytekit import PythonInstanceTask, lazy_module
from flytekit.core.context_manager import FlyteContext
from flytekit.extend import Interface
from flytekit.loggers import logger
from flytekit.types.file.file import FlyteFile
from flytekit.types.schema import FlyteSchema

ge = lazy_module("great_expectations")


@dataclass
class BatchRequestConfig(DataClassJsonMixin):
    """
    Use this configuration to configure Batch Request. A BatchRequest can either be
    a simple BatchRequest or a RuntimeBatchRequest.

    Args:
        data_connector_query: query to request data batch
        runtime_parameters: parameters to be passed at runtime
        batch_identifiers: identifiers to identify the data batch
        batch_spec_passthrough: reader method if your file doesn't have an extension
    """

    data_connector_query: Optional[Dict[str, Any]] = None
    runtime_parameters: Optional[Dict[str, Any]] = None
    batch_identifiers: Optional[Dict[str, str]] = None
    batch_spec_passthrough: Optional[Dict[str, Any]] = None


class GreatExpectationsTask(PythonInstanceTask[BatchRequestConfig]):
    """
    This task can be used to validate your data.
    You can use this when you want to validate your data within the task or workflow.
    If you want to validate your data as and when the type is given, use the `GreatExpectationsType`.

    Args:
        name: name of the task
        datasource_name: tell where your data lives and how to get it
        expectation_suite_name: suite which consists of the data expectations
        data_connector_name: connector to identify data batches
        inputs: inputs to pass to the execute() method
        data_asset_name: name of the data asset (to be used for RuntimeBatchRequest)
        local_file_path: dataset file path useful for FlyteFile and FlyteSchema
        checkpoint_params: optional SimpleCheckpoint parameters
        task_config: batchrequest config
        context_root_dir: directory in which GreatExpectations' configuration resides

