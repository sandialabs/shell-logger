#!/usr/bin/env python3

# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# http://www.sphinx-doc.org/en/master/config

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
from pathlib import Path
import sys

sys.path.append(str(Path.cwd().parent.parent.resolve() / "src"))

# -- Project information -----------------------------------------------------

project = "ShellLogger"
copyright = "2021, Sandia National Laboratories"
author = "Josh Braun, David Collins, Jason M. Gates"
version = "1.0.0"
release = version


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named `sphinx.ext.*`) or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.coverage",
    "sphinx.ext.intersphinx",
    "sphinx.ext.mathjax",
    "sphinx.ext.napoleon",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
    "sphinxarg.ext",
    "sphinx_rtd_theme",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"

# -- AutoDoc Configuration ---------------------------------------------------

autodoc_default_options = {
    "show-inheritance": True,
    "members": True,
    "undoc-members": True
}
autoclass_content = "both"
autodoc_preserve_defaults = True
autodoc_inherit_docstrings = False
todo_include_todos = True
