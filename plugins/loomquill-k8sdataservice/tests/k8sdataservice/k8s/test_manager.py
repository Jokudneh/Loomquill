import unittest
from unittest.mock import MagicMock, patch
from flytekitplugins.k8sdataservice.k8s.manager import K8sManager, DEFAULT_RESOURCES
from kubernetes.client import V1ResourceRequirements
from kubernetes.client.rest import ApiException
from kubernetes.client import V1DeleteOptions
from flytekit import logger


class TestK8sManager(unittest.TestCase):

    def setUp(self):
        self.k8s_manager = K8sManager()
        self.k8s_manager.set_configs({
            "Cluster": "ei-dev2",
            "Name": "test-name",
            "Image": "test-image",
            "Command": ["echo", "hello"],
            "Replicas": 1,
            "Limits": {"cpu": "2", "memory": "4G"},
            "Requests": {"cpu": "1", "memory": "2G"},
        })

    @patch("flytekitplugins.k8sdataservice.k8s.manager.K8sManager.create_service", return_value="test-service")
    @patch("flytekitplugins.k8sdataservice.k8s.manager.K8sManager.create_stateful_set", return_value="test-statefulset")
    def test_create_data_service(self, mock_create_stateful_set, mock_create_service):
        response = self.k8s_manager.create_data_service()
        mock_create_service.assert_called_once()
        mock_create_stateful_set.assert_called_once()
        self.assertEqual(response, "test-statefulset")

    @patch("flytekitplugins.k8sdataservice.k8s.manager.client.AppsV1Api.create_namespaced_stateful_set")
    def test_create_stateful_set(self, mock_create_namespaced_stateful_set):
        mock_metadata = MagicMock()
        mock_metadata.name = "test-statefulset"
        mock_create_namespaced_stateful_set.return_value = MagicMock(metadata=mock_metadata)
        stateful_set_object = self.k8s_manager.create_stateful_set_object()
        response = self.k8s_manager.create_stateful_set(stateful_set_object)
        self.assertEqual(response, "test-statefulset")

    @patch("flytekitplugins.k8sdataservice.k8s.manager.client.AppsV1Api.create_namespaced_stateful_set")
    @patch("flytekitplugins.k8sdataservice.k8s.manager.logger")
    def test_create_stateful_set_failure(self, mock_logger, mock_create_namespaced_stateful_set):
        mock_create_namespaced_stateful_set.side_effect = ApiException("Create failed")
        stateful_set_object = self.k8s_manager.create_stateful_set_object()
        with self.assertRaises(ApiException):
            self.k8s_manager.create_stateful_set(stateful_set_object)
        mock_logger.error.assert_called_once()
        logged_message = mock_logger.error.call_args[0][0]
        self.assertIn("Exception when calling AppsV1Api->create_namespaced_stateful_set: (Create failed)", logged_message)

