"""
Configuration file for the Sphinx documentation builder.

For the full list of built-in configuration values, see the documentation:
https://www.sphinx-doc.org/en/master/usage/configuration.html
"""

import sys
from pathlib import Path

sys.path.append(str(Path.cwd().parent.parent.resolve() / "shell_logger"))

# -- Project information -----------------------------------------------------

project = "shell-logger"
project_copyright = (
    "2024, National Technology & Engineering Solutions of Sandia, LLC (NTESS)"
)
author = "Josh Braun, David Collins, Jason M. Gates"
version = "3.0.1"
release = version


# -- General configuration ---------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.coverage",
    "sphinx.ext.intersphinx",
    "sphinx.ext.mathjax",
    "sphinx.ext.napoleon",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
    "sphinxarg.ext",
    "sphinx_autodoc_typehints",
    "sphinx_copybutton",
    "sphinx_rtd_theme",
    "sphinxcontrib.programoutput",
]
intersphinx_mapping = {"python": ("https://docs.python.org/3", None)}

templates_path = ["_templates"]


# -- Options for HTML output -------------------------------------------------

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

# -- AutoDoc Configuration ---------------------------------------------------

autodoc_default_options = {
    "show-inheritance": True,
    "members": True,
    "undoc-members": True,
}
autoclass_content = "both"
autodoc_preserve_defaults = True
autodoc_inherit_docstrings = False
todo_include_todos = True
