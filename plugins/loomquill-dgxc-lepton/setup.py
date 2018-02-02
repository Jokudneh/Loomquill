from setuptools import setup

PLUGIN_NAME = "dgxc-lepton"

microlib_name = f"flytekitplugins-{PLUGIN_NAME}"

# leptonai 0.47 removed leptonai.api.v1, which the connector imports.
plugin_requires = ["flytekit>=1.9.1,<2.0.0", "leptonai<0.47"]

__version__ = "0.0.0+develop"

setup(
    name=microlib_name,
    version=__version__,
    author="Anshul Jindal",
