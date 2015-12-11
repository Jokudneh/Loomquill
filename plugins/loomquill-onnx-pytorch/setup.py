from setuptools import setup

PLUGIN_NAME = "onnxpytorch"

microlib_name = f"flytekitplugins-{PLUGIN_NAME}"

plugin_requires = [
    "flytekit>=1.3.0b2,<2.0.0",
    "torch>=1.11.0",
    "onnx-pytorch",
    "networkx<3.2; python_version<'3.9'",
    "onnxscript",
    "numpy<2.0.0",
]

