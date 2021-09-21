#!/usr/bin/env bash

# Remove existing documentation to ensure we build from scratch.
if [ -e html ]; then
  rm -rf html
fi

# Build the Sphinx documentation for `ShellLogger`.
sphinx-build -b html source/ html/ -W
