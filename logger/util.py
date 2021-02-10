#!/usr/bin/env python3
from collections.abc import Iterable, Mapping
from io import StringIO
import itertools
import numpy as np
import matplotlib.pyplot as pyplot
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
import os
import subprocess
import sys
import time
from threading import Thread
from types import SimpleNamespace

def program_exists_in_path(program):
    if os.name == "posix":
        subprocess.run(f"command -V {program}", shell=True, check=True)
    elif os.name == "nt":
        subprocess.run(f"where {program}", shell=True, check=True)

def run_teed_command(command, **kwargs):
    start = round(time.time() * 1000)
    stdin = None if not kwargs.get("devnull_stdin") else subprocess.DEVNULL
    popen = subprocess.Popen(command,
                             shell=True,
                             stdin=stdin,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             bufsize=4096)
    output = tee(popen.stdout, popen.stderr, **kwargs)
    popen.wait()
    finish = round(time.time() * 1000)
    return SimpleNamespace(
        returncode = popen.returncode,
        args = popen.args,
        stdout = output.stdout_str,
        stderr = output.stderr_str,
        start = start,
        finish = finish,
        wall = finish - start
    )

def make_svg_line_chart(data):
    fig, ax = pyplot.subplots(figsize=(6, 2), dpi=80)
    pyplot.plot(*zip(*data))
    pyplot.yticks(np.arange(0, 110, 10))
    ax.xaxis.set_ticks([])
    ax.yaxis.set_major_locator(MultipleLocator(20))
    ax.yaxis.set_major_formatter(FormatStrFormatter('%d%%'))
    ax.yaxis.set_minor_locator(MultipleLocator(10))
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    string_io = StringIO()
    fig.savefig(string_io, format='svg')
    pyplot.close(fig)
    string_io.seek(0)
    lines = string_io.readlines()
    svg = "".join(itertools.dropwhile(lambda line: "<svg" not in line, lines))
    return svg

def nested_SimpleNamespace_to_dict(object):
    if "_asdict" in dir(object):
        return nested_SimpleNamespace_to_dict(object._asdict())
    elif isinstance(object, (str, bytes, tuple)):
        return object
    elif isinstance(object, Mapping):
        return {k:nested_SimpleNamespace_to_dict(v) for k,v in object.items()}
    elif isinstance(object, Iterable):
        return [nested_SimpleNamespace_to_dict(x) for x in object]
    elif isinstance(object, SimpleNamespace):
        return nested_SimpleNamespace_to_dict(object.__dict__)
    else:
        return object

def tee(stdout, stderr, **kwargs):
    sys_stdout = None if kwargs.get("quiet_stdout") else sys.stdout
    sys_stderr = None if kwargs.get("quiet_stderr") else sys.stderr
    stdout_io = StringIO() if kwargs.get("stdout_str") else None
    stderr_io = StringIO() if kwargs.get("stderr_str") else None
    stdout_path = open(kwargs.get("stdout_path", os.devnull), "a")
    stderr_path = open(kwargs.get("stderr_path", os.devnull), "a")
    stdout_tee = [sys_stdout, stdout_io, stdout_path]
    stderr_tee = [sys_stderr, stderr_io, stderr_path]
    def write(input, outputs):
        chunk = input.read(4096)
        while chunk:
            for output in outputs:
                if output is not None:
                    output.write(chunk.decode())
            chunk = input.read(4096)
    threads = [
        Thread(target=write, args=(stdout, stdout_tee)),
        Thread(target=write, args=(stderr, stderr_tee)),
    ]
    for thread in threads:
        thread.daemon = True
        thread.start()
    for thread in threads:
        thread.join()
    stdout_str = stdout_io.getvalue() if stdout_io is not None else None
    stderr_str = stderr_io.getvalue() if stderr_io is not None else None
    for file in (stdout_tee + stderr_tee):
        if file not in [None, sys.stdout, sys.stderr, sys.stdin]:
            if not file.closed:
                file.close()
    return SimpleNamespace(
        stdout_str = stdout_str,
        stderr_str = stderr_str
    )

