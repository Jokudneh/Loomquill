from setuptools import setup

PLUGIN_NAME = "athena"

microlib_name = f"flytekitplugins-{PLUGIN_NAME}"

plugin_requires = ["flytekit>=1.3.0b2,<2.0.0"]

__version__ = "0.0.0+develop"

setup(
    title="AWS Athena",
    title_expanded="Flytekit AWS Athena Plugin",
    name=microlib_name,
    version=__version__,
    author="flyteorg",
    author_email="admin@flyte.org",
