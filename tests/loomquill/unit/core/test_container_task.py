import os
import sys
from collections import OrderedDict
from typing import Tuple

import pytest
from kubernetes.client.models import (
    V1Affinity,
    V1Container,
    V1NodeAffinity,
    V1NodeSelectorRequirement,
    V1NodeSelectorTerm,
    V1PodSpec,
    V1PreferredSchedulingTerm,
    V1ResourceRequirements,
    V1Toleration,
)

from flytekit import kwtypes, task, workflow
from flytekit.configuration import Image, ImageConfig, SerializationSettings
from flytekit.core.container_task import ContainerTask
from flytekit.core.pod_template import PodTemplate
from flytekit.image_spec.image_spec import ImageBuildEngine, ImageSpec
from flytekit.tools.translator import get_serializable_task


@pytest.mark.skipif(
    sys.platform in ["darwin", "win32"],
    reason="Skip if running on windows or macos due to CI Docker environment setup failure",
)
def test_local_execution():
    calculate_ellipse_area_python_template_style = ContainerTask(
        name="calculate_ellipse_area_python_template_style",
        input_data_dir="/var/inputs",
        output_data_dir="/var/outputs",
        inputs=kwtypes(a=float, b=float),
        outputs=kwtypes(area=float, metadata=str),
        image="ghcr.io/flyteorg/rawcontainers-python:v2",
        command=[
            "python",
            "calculate-ellipse-area.py",
            "{{.inputs.a}}",
            "{{.inputs.b}}",
            "/var/outputs",
        ],
    )

    area, metadata = calculate_ellipse_area_python_template_style(a=3.0, b=4.0)
    assert isinstance(area, float)
    assert isinstance(metadata, str)

    # Workflow execution with container task
    @task
    def t1(a: float, b: float) -> Tuple[float, float]:
        return a + b, a * b

    @workflow
    def wf(a: float, b: float) -> Tuple[float, str]:
        a, b = t1(a=a, b=b)
