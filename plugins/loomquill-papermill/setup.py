from setuptools import setup

PLUGIN_NAME = "papermill"

microlib_name = f"flytekitplugins-{PLUGIN_NAME}"

plugin_requires = [
    "flytekit",
    "papermill>=1.2.0",
    "nbconvert>=6.0.7",
    "ipykernel>=5.0.0",
]
