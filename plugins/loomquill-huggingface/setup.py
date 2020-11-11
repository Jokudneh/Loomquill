from setuptools import setup

PLUGIN_NAME = "huggingface"

microlib_name = f"flytekitplugins-{PLUGIN_NAME}"

plugin_requires = ["flytekit>=1.3.0b2", "datasets>=2.4.0"]

__version__ = "0.0.0+develop"

setup(
    title="Hugging Face",
    title_expanded="Flytekit Hugging Face Plugin",
    name=microlib_name,
    version=__version__,
    author="Evan Sadler",
    description="Hugging Face plugin for flytekit",
