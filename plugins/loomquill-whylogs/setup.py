from setuptools import setup

PLUGIN_NAME = "whylogs"

microlib_name = f"flytekitplugins-{PLUGIN_NAME}"

# whylogs is not compatible with numpy 2.0 yet
# `np.unicode_` was removed in the NumPy 2.0 release. Use `np.str_` instead.
plugin_requires = ["flytekit>=1.3.0b2", "whylogs[viz]>=1.1.16", "numpy<2.0"]

__version__ = "0.0.0+develop"
