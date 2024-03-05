#!/usr/bin/env python3
"""A simple example, sending output to the log file and console."""

# © 2024 National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the
# U.S. Government retains certain rights in this software.

# SPDX-License-Identifier: BSD-3-Clause

from pathlib import Path

from shell_logger import ShellLogger

sl = ShellLogger(
    "Hello World HTML and Console", Path.cwd() / f"log_{Path(__file__).stem}"
)
sl.print(
    "This example demonstrates logging information both to the HTML log file "
    "and to the console simultaneously."
)
sl.log(
    "Greet everyone to make them feel welcome.",
    "echo 'Hello World'",
    live_stdout=True,
    live_stderr=True,
)
sl.log(
    "Tell everyone who you are, but from a different directory.",
    "whoami",
    cwd=Path.cwd().parent,
    live_stdout=True,
    live_stderr=True,
)
sl.finalize()
print(f"Open {sl.html_file} to view the log.")
