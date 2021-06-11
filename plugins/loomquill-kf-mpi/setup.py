from setuptools import setup

PLUGIN_NAME = "kfmpi"

microlib_name = f"flytekitplugins-{PLUGIN_NAME}"

plugin_requires = ["flytekit>=1.6.1,<2.0.0"]

__version__ = "0.0.0+develop"

setup(
    title="Kubeflow MPI",
    title_expanded="Flytekit Kubeflow MPI Plugin",
