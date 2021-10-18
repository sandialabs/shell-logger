#!/usr/bin/env python3

from pathlib import Path
from shelllogger import ShellLogger

sl = ShellLogger("Hello World HTML with Stats",
                 Path.cwd() / f"log_{Path(__file__).stem}")
sl.print("This example demonstrates logging information solely to the HTML "
         "log file, while collecting CPU, memory, and disk statistics at the "
         "same time.")
sl.log("Greet everyone to make them feel welcome.", "echo 'Hello World'",
       measure=["cpu", "memory", "disk"])
sl.log("Tell everyone who you are, but from a different directory.", "whoami",
       cwd=Path.cwd().parent, measure=["cpu", "memory", "disk"])
sl.finalize()
print(f"Open {sl.html_file} to view the log.")
