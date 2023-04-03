from warnings import warn

from kubernetes.client import V1Container, V1EmptyDirVolumeSource, V1PodSpec, V1Volume, V1VolumeMount

from flytekit.core.pod_template import PodTemplate


def add_shared_mem_volume_to_pod_template(pod_template: PodTemplate) -> None:
    """Add shared memory volume and volume mount to the pod template."""

    warn(
        "Configuring shared memory via `@task(task_config=Elastic(..., increase_shared_mem=True))` or "
        "`PyTorch(..., increase_shared_mem=True)` is deprecated. Use `@task(shared_memory=True)` instead."
    )

