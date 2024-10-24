from setuptools import setup

PLUGIN_NAME = "kfpytorch"

microlib_name = f"flytekitplugins-{PLUGIN_NAME}"

plugin_requires = ["cloudpickle", "flyteidl>=1.5.1", "flytekit>=1.6.1", "kubernetes"]

__version__ = "0.0.0+develop"

setup(
    title="Kubeflow PyTorch",
    title_expanded="Flytekit Kubeflow PyTorch Plugin",
    name=microlib_name,
    version=__version__,
    author="flyteorg",
    author_email="admin@flyte.org",
    description="K8s based Pytorch plugin for Flytekit",
    namespace_packages=["flytekitplugins"],
