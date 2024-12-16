from setuptools import setup

PLUGIN_NAME = "pandera"

microlib_name = f"flytekitplugins-{PLUGIN_NAME}"

plugin_requires = ["flytekit>=1.15.0b2,<2.0.0", "pandera>=0.7.1", "pandas", "great_tables"]

__version__ = "0.0.0+develop"

setup(
    title="Pandera",
    title_expanded="Flytekit Pandera Plugin",
    name=microlib_name,
    version=__version__,
    author="flyteorg",
    author_email="admin@flyte.org",
    description="Pandera plugin for flytekit",
