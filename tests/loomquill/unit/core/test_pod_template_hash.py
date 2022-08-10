import unittest

from kubernetes.client import V1PodSpec, V1Container

from flytekit import PodTemplate, task, ImageSpec
from flytekit.configuration import SerializationSettings, ImageConfig, Image


class TestPodTemplateHashing(unittest.TestCase):
    """Test suite for PodTemplate.version_hash()."""

    def test_default_initialization_hash_consistency(self):
        """Tests that default PodTemplates have consistent hashes."""
        pt1 = PodTemplate()
        pt2 = PodTemplate()
        self.assertEqual(pt1.version_hash(), pt2.version_hash())

    def test_identical_complex_objects_hash_consistency(self):
        """Tests that identical complex PodTemplates have the same hash."""
        common_pod_spec = V1PodSpec(
            containers=[
                V1Container(name="c1", image="img1:latest", command=["/bin/sh", "-c", "echo hello"]),
                V1Container(name="c2", image=ImageSpec(name="img2-repo/img2:v1.0"))
            ],
            restart_policy="Never",
            node_selector={"disktype": "ssd"}
        )
        pt1 = PodTemplate(
            pod_spec=common_pod_spec,
            primary_container_name="c1",
            labels={"app": "myapp", "env": "prod"},
            annotations={"author": "tester", "version": "1.2.3"}
        )
        pt2 = PodTemplate(
            pod_spec=common_pod_spec,  # Same instance, but could be an identical copy
            primary_container_name="c1",
            labels={"app": "myapp", "env": "prod"},  # Same content
            annotations={"author": "tester", "version": "1.2.3"}  # Same content
