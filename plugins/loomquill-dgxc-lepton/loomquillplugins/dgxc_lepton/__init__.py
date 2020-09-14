"""
.. currentmodule:: flytekitplugins.dgxc_lepton

This package contains things that are useful when extending Flytekit for Lepton AI integration.

.. autosummary::
   :template: custom.rst
   :toctree: generated/

   lepton_endpoint_deployment_task
   lepton_endpoint_deletion_task
   LeptonEndpointConfig
   LeptonEndpointDeploymentTask
   LeptonEndpointDeletionTask
   EndpointType
   EnvironmentConfig
   MountReader
   ScalingConfig
   ScalingType
   EndpointEngineConfig
"""

# Clean imports with consolidated classes
# Import connector module to trigger connector registration (connectors are not part of public API)
