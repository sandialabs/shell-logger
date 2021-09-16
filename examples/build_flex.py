#!/usr/bin/env python3

from pathlib import Path
from shelllogger import ShellLogger

sl = ShellLogger("Build Flex",
                 Path.cwd() / f"log_{Path(__file__).stem}")
sl.print("This example demonstrates cloning, configuring, and building the "
         "Flex tool.")
sl.log("Clone the Flex repository.",
       "git clone --depth 1 --branch flex-2.5.39 "
       "https://github.com/westes/flex.git flex-2.5.39", live_stdout=True,
       live_stderr=True)
sl.log("Run Autogen", "./autogen.sh", cwd=Path.cwd()/"flex-2.5.39",
       live_stdout=True, live_stderr=True)
sl.log("Configure Flex", "./configure --prefix=$(dirname $(pwd))/flex",
       cwd=Path.cwd()/"flex-2.5.39", live_stdout=True, live_stderr=True,
       measure=["cpu", "memory", "disk"])
sl.log("Build libcompat.la", "make libcompat.la",
       cwd=Path.cwd()/"flex-2.5.39/lib", live_stdout=True, live_stderr=True,
       measure=["cpu", "memory", "disk"])
sl.log("Build & Install Flex", "make install-exec",
       cwd=Path.cwd()/"flex-2.5.39", live_stdout=True, live_stderr=True,
       measure=["cpu", "memory", "disk"])
sl.finalize()
print(f"Open {sl.html_file} to view the log.")
