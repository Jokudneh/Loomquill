from setuptools import setup

PLUGIN_NAME = "flyteinteractive"

microlib_name = f"flytekitplugins-{PLUGIN_NAME}"

plugin_requires = ["flytekit>=1.1.0b0,<2.0.0", "jupyter"]

__version__ = "0.0.0+develop"

setup(
    title="Flyte Interactive",
    title_expanded="Flytekit FlyteInteractive Plugin",
    name=microlib_name,
