from setuptools import setup

PLUGIN_NAME = "omegaconf"

microlib_name = f"flytekitplugins-{PLUGIN_NAME}"

plugin_requires = ["flytekit>=1.10.0,<2.0.0", "flatten-dict", "omegaconf>=2.3.0"]

__version__ = "0.0.0+develop"

setup(
    title="OmegaConf",
    title_expanded="Flytekit OmegaConf Plugin",
    name=microlib_name,
    version=__version__,
    author="flyteorg",
    author_email="admin@flyte.org",
    description="OmegaConf plugin for Flytekit",
    url="https://github.com/flyteorg/flytekit/tree/master/plugins/flytekit-omegaconf",
