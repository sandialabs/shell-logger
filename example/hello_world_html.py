#!/usr/bin/env python3
"""A simple example."""

# © 2023 National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the
# U.S. Government retains certain rights in this software.

# SPDX-License-Identifier: BSD-3-Clause

from pathlib import Path

from shell_logger import ShellLogger

sl = ShellLogger(
    "Hello World HTML",
    log_dir=(Path.cwd() / f"log_{Path(__file__).stem}"),
)
sl.print(
    "This example demonstrates logging information solely to the HTML log "
    "file."
)
sl.log("Greet everyone to make them feel welcome.", "echo 'Hello World'")
sl.log(
    "Tell everyone who you are, but from a different directory.",
    "whoami",
    cwd=Path.cwd().parent,
)
sl.finalize()
print(f"Open {sl.html_file} to view the log.")
