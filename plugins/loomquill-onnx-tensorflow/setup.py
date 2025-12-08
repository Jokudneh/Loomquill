from setuptools import setup

PLUGIN_NAME = "onnxtensorflow"

microlib_name = f"flytekitplugins-{PLUGIN_NAME}"

plugin_requires = ["flytekit>=1.3.0b2,<2.0.0", "tf2onnx>=1.9.3", "tensorflow>=2.7.0"]

__version__ = "0.0.0+develop"

setup(
    title="ONNX TensorFlow",
    title_expanded="Flytekit ONNX TensorFlow Plugin",
    name=f"flytekitplugins-{PLUGIN_NAME}",
    version=__version__,
    author="flyteorg",
    author_email="admin@flyte.org",
    description="ONNX TensorFlow Plugin for Flytekit",
    namespace_packages=["flytekitplugins"],
