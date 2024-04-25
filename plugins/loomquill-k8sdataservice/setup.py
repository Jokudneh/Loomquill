from setuptools import find_namespace_packages, setup

PLUGIN_NAME = "k8sdataservice"

microlib_name = f"flytekitplugins-{PLUGIN_NAME}"

plugin_requires = ["flytekit>=1.11.0,<2.0.0", "kubernetes>=23.6.0,<24.0.0", "flyteidl>=1.11.0,<2.0.0"]

__version__ = "0.0.0+develop"

setup(
    title="Kubernetes Stateful",
    title_expanded="K8s Stateful Service Plugin",
    name=microlib_name,
