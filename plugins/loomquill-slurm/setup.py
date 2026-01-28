from setuptools import setup

PLUGIN_NAME = "slurm"

microlib_name = f"flytekitplugins-{PLUGIN_NAME}"

plugin_requires = ["flytekit>=1.15.0", "flyteidl>=1.15.0", "asyncssh"]

__version__ = "0.0.0+develop"

setup(
    title="Slurm",
    title_expanded="Flytekit Slurm Plugin",
    name=microlib_name,
    version=__version__,
    author="flyteorg",
    author_email="admin@flyte.org",
    description="This package holds the Slurm plugins for flytekit",
    namespace_packages=["flytekitplugins"],
    packages=[
        f"flytekitplugins.{PLUGIN_NAME}",
        f"flytekitplugins.{PLUGIN_NAME}.script",
