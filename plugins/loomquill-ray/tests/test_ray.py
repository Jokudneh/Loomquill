import base64
import json

import ray
import yaml

from flytekit.core.resources import convert_resources_to_resource_model, pod_spec_from_resources
from flytekitplugins.ray import HeadNodeConfig
from flytekitplugins.ray.models import (
    AutoscalerOptions,
    HeadGroupSpec,
    RayCluster,
    RayJob,
    WorkerGroupSpec,
)
from flytekitplugins.ray.task import AutoscalerOptionsConfig, RayJobConfig, WorkerNodeConfig
from google.protobuf.json_format import MessageToDict

from flytekit import PythonFunctionTask, task, PodTemplate, Resources
from flytekit.configuration import Image, ImageConfig, SerializationSettings
from flytekit.models.task import K8sPod


pod_template=PodTemplate(
        primary_container_name="primary",
        labels={"lKeyA": "lValA"},
        annotations={"aKeyA": "aValA"},
    )

config = RayJobConfig(
    worker_node_config=[
        WorkerNodeConfig(
            group_name="test_group",
            replicas=3,
            min_replicas=0,
            max_replicas=10,
            pod_template=pod_template,
        )
    ],
    head_node_config=HeadNodeConfig(requests=Resources(cpu="1", mem="1Gi"), limits=Resources(cpu="2", mem="2Gi")),
    runtime_env={"pip": ["numpy"]},
    enable_autoscaling=True,
    autoscaler_options=AutoscalerOptionsConfig(
        upscaling_mode=AutoscalerOptionsConfig.UpscalingMode.CONSERVATIVE,
        idle_timeout_seconds=120,
        image="rayproject/ray:2.9.0",
        env={"lKeyA": "lValA"},
        requests=Resources(cpu="1", mem="1Gi"),
        limits=Resources(cpu="2", mem="2Gi"),
    ),
    shutdown_after_job_finishes=True,
    ttl_seconds_after_finished=20,
)

