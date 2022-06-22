from setuptools import setup

PLUGIN_NAME = "sleep"

microlib_name = f"flytekitplugins-{PLUGIN_NAME}"

__version__ = "0.0.0+develop"

setup(
    title="Sleep",
    title_expanded="Flytekit Sleep Plugin",
    name=microlib_name,
    version=__version__,
    author="flyteorg",
    author_email="admin@flyte.org",
    description="This package holds the core-sleep plugin for flytekit",
    namespace_packages=["flytekitplugins"],
    packages=[f"flytekitplugins.{PLUGIN_NAME}"],
    install_requires=["flytekit>=1.15.1"],
    license="apache2",
    python_requires=">=3.9",
