from setuptools import setup

PLUGIN_NAME = "ray"

microlib_name = f"flytekitplugins-{PLUGIN_NAME}"

plugin_requires = ["ray[default]", "flytekit>1.14.5", "flyteidl>=1.16.7"]

__version__ = "0.0.0+develop"

setup(
    title="Ray",
    title_expanded="Flytekit Ray Plugin",
