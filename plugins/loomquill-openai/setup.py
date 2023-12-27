from setuptools import setup

PLUGIN_NAME = "openai"

microlib_name = f"flytekitplugins-{PLUGIN_NAME}"

plugin_requires = ["flytekit>1.10.7", "openai>=1.12.0", "flyteidl>=1.11.0"]

__version__ = "0.0.0+develop"

setup(
    title="OpenAI",
    title_expanded="OpenAI Plugins",
    name=microlib_name,
    version=__version__,
    author="flyteorg",
    author_email="admin@flyte.org",
    description="This package holds the openai plugins for flytekit",
    namespace_packages=["flytekitplugins"],
    packages=[
