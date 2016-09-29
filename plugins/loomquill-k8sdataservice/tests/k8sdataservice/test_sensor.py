import pytest
import asyncio
import unittest
from unittest.mock import patch, MagicMock
from kubernetes import client
from kubernetes.client.rest import ApiException
from flytekitplugins.k8sdataservice.sensor import CleanupSensor


@pytest.mark.asyncio
@patch("flytekitplugins.k8sdataservice.sensor.KubeConfig")
@patch("flytekitplugins.k8sdataservice.sensor.client.AppsV1Api")
@patch("flytekitplugins.k8sdataservice.sensor.client.CoreV1Api")
@patch("flytekitplugins.k8sdataservice.sensor.client.CustomObjectsApi")
@patch("flytekitplugins.k8sdataservice.sensor.logger")
async def test_poke_no_cleanup(
    mock_logger,
    mock_custom_api,
    mock_core_v1_api,
    mock_apps_v1_api,
    mock_kube_config
):
    mock_kube_config.return_value = MagicMock()
    sensor = CleanupSensor(name="test-sensor")
    await asyncio.create_task(
        sensor.poke(release_name="test-release",
                    cleanup_data_service=False,
