#!/usr/bin/env python3
from collections.abc import Iterable, Mapping
from io import StringIO
import itertools
import numpy as np
import matplotlib.pyplot as pyplot
import os
import subprocess
import sys
import time
from threading import Thread
from types import SimpleNamespace

def checkIfProgramExistsInPath(program):
    if os.name == "posix":
        subprocess.run(f"command -V {program}", shell=True, check=True)
    elif os.name == "nt":
        subprocess.run(f"where {program}", shell=True, check=True)

def runCommandWithConsole(command, **kwargs):
    start = round(time.time() * 1000)
    stdin = None if not kwargs.get("devnull_stdin") else subprocess.DEVNULL
    popen = subprocess.Popen(command,
                             shell=True,
                             stdin=stdin,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
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

def makeSVGLineChart(data):
    fig = pyplot.figure()
    pyplot.plot(*zip(*data))
    pyplot.yticks(np.arange(0, 110, 10))
    stringIO = StringIO()
    fig.savefig(stringIO, format='svg')
    pyplot.close(fig)
    stringIO.seek(0)
    lines = stringIO.readlines()
    svg = "".join(itertools.dropwhile(lambda line: "<svg" not in line, lines))
    return svg

def nestedSimpleNamespaceToDict(object):
    if "_asdict" in dir(object):
        return nestedSimpleNamespaceToDict(object._asdict())
    elif isinstance(object, (str, bytes, tuple)):
        return object
    elif isinstance(object, Mapping):
        return { k:nestedSimpleNamespaceToDict(v) for k, v in object.items() }
    elif isinstance(object, Iterable):
        return [ nestedSimpleNamespaceToDict(x) for x in object ]
    elif isinstance(object, SimpleNamespace):
        return nestedSimpleNamespaceToDict(object.__dict__)
    else:
        return object

def tee(stdout, stderr, **kwargs):
    sys_stdout = open(os.devnull, "a") if kwargs.get("quiet_stdout") else sys.stdout
    sys_stderr = open(os.devnull, "a") if kwargs.get("quiet_stderr") else sys.stderr
    stdout_io = StringIO() if kwargs.get("stdout_str") else open(os.devnull, "a")
    stderr_io = StringIO() if kwargs.get("stderr_str") else open(os.devnull, "a")
    stdout_file = open(kwargs.get("stdout_file"), "a") if kwargs.get("stdout_file") else open(os.devnull, "a")
    stderr_file = open(kwargs.get("stderr_file"), "a") if kwargs.get("stderr_file") else open(os.devnull, "a")
    stdout_tee = [sys_stdout, stdout_io, stdout_file]
    stderr_tee = [sys_stderr, stderr_io, stderr_file]
    def write(input, outputs):
        for line in iter(input.readline, b""):
            line = line.decode()
            for output in outputs:
                output.write(line)
    threads = [
        Thread(target=write, args=(stdout, stdout_tee)),
        Thread(target=write, args=(stderr, stderr_tee)),
    ]
    for thread in threads:
        thread.daemon = True
        thread.start()
    for thread in threads:
        thread.join()
    stdout_str = stdout_io.getvalue() if type(stdout_io) is StringIO else None
    stderr_str = stderr_io.getvalue() if type(stderr_io) is StringIO else None
    for file in (stdout_tee + stderr_tee):
        if file not in [None, sys.stdout, sys.stderr, sys.stdin]:
            file.close()
    return SimpleNamespace(
        stdout_str = stdout_str,
        stderr_str = stderr_str
    )

