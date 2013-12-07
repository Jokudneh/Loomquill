from setuptools import setup

PLUGIN_NAME = "onnxtensorflow"

microlib_name = f"flytekitplugins-{PLUGIN_NAME}"

plugin_requires = ["flytekit>=1.3.0b2,<2.0.0", "tf2onnx>=1.9.3", "tensorflow>=2.7.0"]

