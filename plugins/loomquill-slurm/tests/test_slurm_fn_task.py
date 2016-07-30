import os.path
from unittest import mock
from flytekit.core import context_manager
import flytekit
from flytekit import StructuredDataset, StructuredDatasetTransformerEngine, task, ImageSpec
from flytekit.configuration import Image, ImageConfig, SerializationSettings, FastSerializationSettings, DefaultImages
from flytekit.core.context_manager import ExecutionParameters, FlyteContextManager, ExecutionState
from flytekitplugins.slurm import SlurmFunctionConfig


def test_slurm_task():
    script_file = """#!/bin/bash -i
