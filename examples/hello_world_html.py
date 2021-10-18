#!/usr/bin/env python3

from pathlib import Path
from shelllogger import ShellLogger

sl = ShellLogger("Hello World HTML",
                 Path.cwd() / f"log_{Path(__file__).stem}")
sl.print("This example demonstrates logging information solely to the HTML "
         "log file.")
sl.log("Greet everyone to make them feel welcome.", "echo 'Hello World'")
sl.log("Tell everyone who you are, but from a different directory.", "whoami",
       cwd=Path.cwd().parent)
sl.finalize()
print(f"Open {sl.html_file} to view the log.")
