#!/usr/bin/env python3

from pathlib import Path
from shelllogger import ShellLogger

sl = ShellLogger("Hello ShellLogger",
                 Path.cwd() / f"log_{Path(__file__).stem}")
sl.print("This example demonstrates logging information both to the HTML log "
         "file and to the console simultaneously.")
sl.log("Greet everyone to make them feel welcome.", "echo 'Hello World'",
       live_stdout=True, live_stderr=True)
sl.log("Tell everyone who you are, but from a different directory.", "whoami",
       cwd=Path.cwd().parent, live_stdout=True, live_stderr=True)
sl.finalize()
print(f"Open {sl.html_file} to view the log.")
