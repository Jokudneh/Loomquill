from setuptools import setup

PLUGIN_NAME = "flyteinteractive"

microlib_name = f"flytekitplugins-{PLUGIN_NAME}"

plugin_requires = ["flytekit>=1.1.0b0,<2.0.0", "jupyter"]

__version__ = "0.0.0+develop"

setup(
    title="Flyte Interactive",
    title_expanded="Flytekit FlyteInteractive Plugin",
    name=microlib_name,
    version=__version__,
    author="flyteorg",
    author_email="admin@flyte.org",
    description="This package holds the flyteinteractive plugins for flytekit",
    namespace_packages=["flytekitplugins"],
