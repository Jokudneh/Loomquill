from setuptools import setup

PLUGIN_NAME = "sleep"

microlib_name = f"flytekitplugins-{PLUGIN_NAME}"

__version__ = "0.0.0+develop"

setup(
    title="Sleep",
    title_expanded="Flytekit Sleep Plugin",
    name=microlib_name,
