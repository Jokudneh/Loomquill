from setuptools import setup

PLUGIN_NAME = "envd"

microlib_name = f"flytekitplugins-{PLUGIN_NAME}"

plugin_requires = ["flytekit>=1.12.0", "envd"]

__version__ = "0.0.0+develop"

setup(
    title="Envd",
    title_expanded="Flytekit Envd Plugin",
    name=microlib_name,
    version=__version__,
    author="flyteorg",
    author_email="admin@flyte.org",
    description="This package enables users to easily build a Docker image for tasks or workflows.",
    namespace_packages=["flytekitplugins"],
