from setuptools import setup

PLUGIN_NAME = "inference"

microlib_name = f"flytekitplugins-{PLUGIN_NAME}"

plugin_requires = ["flytekit>=1.13.0,<2.0.0", "kubernetes", "openai"]

__version__ = "0.0.0+develop"

setup(
    title="Inference",
    title_expanded="Inference Plugins",
    name=microlib_name,
    version=__version__,
    author="flyteorg",
    author_email="admin@flyte.org",
    description="This package enables seamless use of model inference sidecar services within Flyte",
