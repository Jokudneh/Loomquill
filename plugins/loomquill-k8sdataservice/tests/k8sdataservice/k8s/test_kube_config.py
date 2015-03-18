import unittest
from unittest.mock import patch
from flytekitplugins.k8sdataservice.k8s.kube_config import KubeConfig
from kubernetes.config import ConfigException


class TestKubeConfig(unittest.TestCase):

    @patch("flytekitplugins.k8sdataservice.k8s.kube_config.config.load_incluster_config")
