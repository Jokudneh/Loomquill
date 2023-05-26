"""Test functionality that is shared between the pytorch and pytorch-elastic tasks."""

from contextlib import nullcontext
from typing import Union

import pytest
from flytekitplugins.kfpytorch.task import Elastic, PyTorch
from kubernetes.client import V1Container, V1EmptyDirVolumeSource, V1PodSpec, V1Volume, V1VolumeMount

from flytekit import PodTemplate, task


@pytest.mark.parametrize(
    "task_config, pod_template, needs_shm_volume, raises",
    [
        # Test that by default shared memory volume is added
        (PyTorch(num_workers=3), None, True, False),
        (Elastic(nnodes=2, increase_shared_mem=True), None, True, False),
        # Test disabling shared memory volume
        (PyTorch(num_workers=3, increase_shared_mem=False), None, False, False),
        (Elastic(nnodes=2, increase_shared_mem=False), None, False, False),
        # Test that explicitly passed pod template does not break adding shm volume
        (Elastic(nnodes=2, increase_shared_mem=True), PodTemplate(), True, False),
        # Test that pod template with container does not break adding shm volume
        (
            Elastic(nnodes=2),
            PodTemplate(
                pod_spec=V1PodSpec(containers=[V1Container(name="primary")]),
            ),
            True,
            False,
        ),
        # Test that pod template with volume/volume mount does not break adding shm volume
        (
            Elastic(nnodes=2),
            PodTemplate(
                pod_spec=V1PodSpec(
                    containers=[
                        V1Container(name="primary", volume_mounts=[V1VolumeMount(name="foo", mount_path="/bar")])
