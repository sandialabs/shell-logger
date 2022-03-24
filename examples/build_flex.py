#!/usr/bin/env python3

from pathlib import Path
from shelllogger import ShellLogger

sl = ShellLogger("Build Flex", Path.cwd() / f"log_{Path(__file__).stem}")
sl.print(
    "This example demonstrates cloning, configuring, and building the Flex "
    "tool."
)
FLEX_VERSION = "flex-2.5.39"
sl.log(
    "Clone the Flex repository.",
    f"git clone --depth 1 --branch {FLEX_VERSION} "
    f"https://github.com/westes/flex.git {FLEX_VERSION}",
    live_stdout=True,
    live_stderr=True
)
sl.log(
    "Run `autogen`.",
    "./autogen.sh",
    cwd=Path.cwd() / FLEX_VERSION,
    live_stdout=True,
    live_stderr=True
)
measure = ["cpu", "memory", "disk"]
sl.log(
    "Configure flex.",
    "./configure --prefix=$(dirname $(pwd))/flex",
    cwd=Path.cwd() / FLEX_VERSION,
    live_stdout=True,
    live_stderr=True,
    measure=measure
)
sl.log(
    "Build `libcompat.la`.",
    "make libcompat.la",
    cwd=Path.cwd() / f"{FLEX_VERSION}/lib",
    live_stdout=True,
    live_stderr=True,
    measure=measure
)
sl.log(
    "Build & install flex.",
    "make install-exec",
    cwd=Path.cwd() / FLEX_VERSION,
    live_stdout=True,
    live_stderr=True,
    measure=measure
)
sl.finalize()
print(f"Open {sl.html_file} to view the log.")
