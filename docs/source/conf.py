# -*- coding: utf-8 -*-
#
# Configuration file for the Sphinx documentation builder.
#
# This file does only contain a selection of the most common options. For a
# full list see the documentation:
# http://www.sphinx-doc.org/en/stable/config

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys

flytekit_dir = os.path.abspath("../..")
flytekit_src_dir = os.path.abspath(os.path.join(flytekit_dir, "flytekit"))
plugins_dir = os.path.abspath(os.path.join(flytekit_dir, "plugins"))

for possible_plugin_dir in os.listdir(plugins_dir):
    dir_path = os.path.abspath((os.path.join(plugins_dir, possible_plugin_dir)))
    plugin_path = os.path.abspath(os.path.join(dir_path, "flytekitplugins"))
    if os.path.isdir(dir_path) and os.path.exists(plugin_path):
        sys.path.insert(0, dir_path)

sys.path.insert(0, flytekit_src_dir)
sys.path.insert(0, flytekit_dir)

# -- Project information -----------------------------------------------------

project = "Flytekit"
copyright = "2023, Flyte"
author = "Flyte"

# The full version, including alpha/beta/rc tags
release = "0.16.0b9"

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.napoleon",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
