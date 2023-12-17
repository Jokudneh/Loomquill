from setuptools import setup

PLUGIN_NAME = "kftensorflow"

microlib_name = f"flytekitplugins-{PLUGIN_NAME}"

plugin_requires = ["flyteidl>=1.10.0", "flytekit>=1.6.1"]

__version__ = "0.0.0+develop"

setup(
    title="Kubeflow TensorFlow",
    title_expanded="Flytekit Kubeflow TensorFlow Plugin",
    name=microlib_name,
    version=__version__,
    author="flyteorg",
    author_email="admin@flyte.org",
