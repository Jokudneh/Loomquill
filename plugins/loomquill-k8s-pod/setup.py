from setuptools import setup

PLUGIN_NAME = "pod"

microlib_name = f"flytekitplugins-{PLUGIN_NAME}"

plugin_requires = [
    "flytekit>=1.3.0b2",
    "kubernetes>=12.0.1",
]

__version__ = "0.0.0+develop"

setup(
    title="Kubernetes Pod",
    title_expanded="Flytekit Kubernetes Pod Plugin",
    name=microlib_name,
    version=__version__,
