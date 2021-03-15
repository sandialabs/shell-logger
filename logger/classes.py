#!/usr/bin/env python3
from abc import abstractmethod
from collections import namedtuple
import fcntl
from io import StringIO
import inspect
from multiprocessing import Process, Manager
import os
from pathlib import Path
import subprocess
import sys
import _thread
from threading import Thread
import time
from types import SimpleNamespace

def trace_collector(**kwargs):
    trace_name = kwargs["trace"]
    Collectors = [c for c in Trace.subclasses if c.trace_name == trace_name]
    if len(Collectors) == 1:
        Collector = Collectors[0]
        return Collector(**kwargs)
    elif len(Collectors) == 0:
        raise RuntimeError(f"Unsupported trace type: {trace_name}")
    else:
        raise RuntimeError(f"Multiple trace types match {trace_name}")

def stats_collectors(**kwargs):
    collectors = []
    if "measure" in kwargs:
        interval = kwargs["interval"] if "interval" in kwargs else 1.0
        stats = {}
        manager = Manager()
        for Collector in StatsCollector.subclasses:
            if Collector.stat_name in kwargs["measure"]:
                collectors.append(Collector(interval, manager))
    return collectors

class Shell:
    def __init__(self, pwd=Path.cwd()):
        self.aux_stdin_rfd, self.aux_stdin_wfd = os.pipe()
        self.aux_stdout_rfd, self.aux_stdout_wfd = os.pipe()
        self.aux_stderr_rfd, self.aux_stderr_wfd = os.pipe()

        aux_stdout_write_flags = fcntl.fcntl(self.aux_stdout_wfd, fcntl.F_GETFL)
        fcntl.fcntl(self.aux_stdout_wfd,
                    fcntl.F_SETFL,
                    aux_stdout_write_flags | os.O_NONBLOCK)
        aux_stderr_write_flags = fcntl.fcntl(self.aux_stderr_wfd, fcntl.F_GETFL)
        fcntl.fcntl(self.aux_stderr_wfd,
                    fcntl.F_SETFL,
                    aux_stderr_write_flags | os.O_NONBLOCK)

        os.set_inheritable(self.aux_stdout_wfd, True)
        os.set_inheritable(self.aux_stderr_wfd, True)
        self.shell = subprocess.Popen(os.environ.get("SHELL") or "/bin/sh",
                                      stdin=self.aux_stdin_rfd,
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE,
                                      close_fds=False)
        os.set_inheritable(self.aux_stdout_wfd, False)
        os.set_inheritable(self.aux_stderr_wfd, False)
        self.cd(pwd)

    def __del__(self):
        os.close(self.aux_stdin_rfd)
        os.close(self.aux_stdin_wfd)
        os.close(self.aux_stdout_rfd)
        os.close(self.aux_stdout_wfd)
        os.close(self.aux_stderr_rfd)
        os.close(self.aux_stderr_wfd)

    def __eq__(self, other):
        return type(self) == type(other) and self.pwd() == other.pwd()

    def pwd(self):
        directory, _ = self.auxiliary_command(posix="pwd", nt="cd", strip=True)
        return directory

    def cd(self, dir):
        os.chdir(dir)
        self.auxiliary_command(posix=f"cd {dir}", nt=f"cd {dir}")

    def run(self, command, **kwargs):
        start = round(time.time() * 1000)
        if kwargs.get("devnull_stdin"):
            os.write(self.aux_stdin_wfd,
                     f"{{\n{command}\n}} </dev/null\n".encode())
        else:
            os.write(self.aux_stdin_wfd, f"{{\n{command}\n}}\n".encode())
        os.write(self.aux_stdin_wfd, f"RET_CODE=$?\n".encode())
        os.write(self.aux_stdin_wfd, f"printf '\\4'\n".encode())
        os.write(self.aux_stdin_wfd, f"printf '\\4' 1>&2\n".encode())
        try:
            output = self.tee(self.shell.stdout, self.shell.stderr, **kwargs)
        except KeyboardInterrupt:
            os.close(self.aux_stdin_wfd)
            raise RuntimeError(
                f"There was a problem running the command ``{command}''. "
                "This is a fatal error and we cannot continue. Ensure that "
                "the syntax of the command is correct."
            )
        finish = round(time.time() * 1000)
        aux_out, _ = self.auxiliary_command(posix="echo $RET_CODE")
        try:
            returncode = int(aux_out)
        except ValueError:
            returncode = "N/A"
        return SimpleNamespace(
            returncode = returncode,
            args = command,
            stdout = output.stdout_str,
            stderr = output.stderr_str,
            start = start,
            finish = finish,
            wall = finish - start
        )

    def tee(self, stdout, stderr, **kwargs):
        sys_stdout = None if kwargs.get("quiet_stdout") else sys.stdout
        sys_stderr = None if kwargs.get("quiet_stderr") else sys.stderr
        stdout_io = StringIO() if kwargs.get("stdout_str") else None
        stderr_io = StringIO() if kwargs.get("stderr_str") else None
        stdout_path = open(kwargs.get("stdout_path", os.devnull), "a")
        stderr_path = open(kwargs.get("stderr_path", os.devnull), "a")
        stdout_tee = [sys_stdout, stdout_io, stdout_path]
        stderr_tee = [sys_stderr, stderr_io, stderr_path]
        def write(input, outputs):
            chunk = os.read(input.fileno(), 4096)
            while chunk and chunk[-1] != 4:
                for output in outputs:
                    if output is not None:
                        output.write(chunk.decode())
                chunk = os.read(input.fileno(), 4096)
            if not chunk:
                _thread.interrupt_main()
            chunk = chunk[:-1]
            for output in outputs:
                if output is not None:
                    output.write(chunk.decode())
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

    def auxiliary_command(self, **kwargs):
        stdout, stderr = None, None
        cmd = kwargs[os.name]
        out = self.aux_stdout_wfd
        err = self.aux_stderr_wfd
        if os.name in kwargs:
            os.write(self.aux_stdin_wfd, f"{cmd} 1>&{out} 2>&{err}\n".encode())
            os.write(self.aux_stdin_wfd, f"printf '\\4' 1>&{out}\n".encode())
            os.write(self.aux_stdin_wfd, f"printf '\\4' 1>&{err}\n".encode())
            stdout = ""
            stderr = ""
            aux = os.read(self.aux_stdout_rfd, 65536)
            while aux[-1] != 4:
                stdout += aux.decode()
                aux = os.read(self.aux_stdout_rfd, 65536)
            aux = aux[:-1]
            stdout += aux.decode()
            aux = os.read(self.aux_stderr_rfd, 65536)
            while aux[-1] != 4:
                stderr += aux.decode()
                aux = os.read(self.aux_stderr_rfd, 65536)
            aux = aux[:-1]
            stderr += aux.decode()
            if stdout and kwargs.get("strip"):
                stdout = stdout.strip()
                stderr = stderr.strip()
        return stdout, stderr

class Trace:
    trace_name = "undefined"
    subclasses = []
    def subclass(TraceSubclass):
        if (issubclass(TraceSubclass, Trace)):
            Trace.subclasses.append(TraceSubclass)
        return TraceSubclass
    def __init__(self, **kwargs):
        if kwargs.get("trace_path"):
            self.output_path = Path(kwargs["trace_path"])
        else:
            self.output_path = Path(f"{self.trace_name}.log")
    @property
    @abstractmethod
    def trace_args(self):
        raise AbstractMethod()
    def command(self, command, **kwargs):
        return f"{self.trace_args} -- {command}"

class StatsCollector:
    stat_name = "undefined"
    subclasses = []
    def subclass(StatsCollectorSubclass):
        if (issubclass(StatsCollectorSubclass, StatsCollector)):
            StatsCollector.subclasses.append(StatsCollectorSubclass)
        return StatsCollectorSubclass
    def __init__(self, interval, manager):
        self.interval = interval
        self.process = Process(target=self.loop, args=())
    def start(self):
        self.process.start()
    def loop(self):
        while True:
            self.collect()
            time.sleep(self.interval)
    @abstractmethod
    def collect(self):
        raise AbstractMethod()
    @abstractmethod
    def unproxied_stats(self):
        raise AbstractMethod()
    def finish(self):
        self.process.terminate()
        return self.unproxied_stats()

class FileAlreadyExists(RuntimeError):
    def __init__(self, file):
        super().__init__(f"{file.resolve()} already exists! "
                          "Delete or rename and try rerunning this.")

class AbstractMethod(NotImplementedError):
    def __init__(self):
        class_name = inspect.stack()[1].frame.f_locals['self'].__class__.__name__
        method_name = inspect.stack()[1].function
        super().__init__(f"{class_name} must implement {method_name}()")

