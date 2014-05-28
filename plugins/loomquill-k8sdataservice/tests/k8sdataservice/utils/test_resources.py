import unittest
from kubernetes import client
from utils.resources import cleanup_resources, convert_flyte_to_k8s_fields


class TestCleanupResources(unittest.TestCase):

    def test_cleanup_resources(self):
        resources = client.V1ResourceRequirements(
            limits={"cpu": "2", "memory": "10G", "ephemeral_storage": "0", "storage": "0GB"},
            requests={"cpu": "1", "memory": "0", "ephemeral_storage": "5G", "storage": "0"}
        )
        cleanup_resources(resources)
        expected_limits = {"cpu": "2", "memory": "10G"}
        self.assertEqual(resources.limits, expected_limits)

        expected_requests = {"cpu": "1", "ephemeral_storage": "5G"}
        self.assertEqual(resources.requests, expected_requests)

