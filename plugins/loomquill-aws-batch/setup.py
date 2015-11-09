from setuptools import setup

PLUGIN_NAME = "awsbatch"

microlib_name = f"flytekitplugins-{PLUGIN_NAME}"

plugin_requires = ["flytekit>=1.3.0b2"]

__version__ = "0.0.0+develop"

setup(
    title="AWS Batch",
    title_expanded="Flytekit AWS Batch Plugin",
    name=microlib_name,
    version=__version__,
    author="flyteorg",
    author_email="admin@flyte.org",
    description="This package holds the AWS Batch plugins for flytekit",
