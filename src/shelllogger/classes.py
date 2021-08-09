#!/usr/bin/env python3

from __future__ import annotations
from abc import abstractmethod
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
from time import sleep, time
from types import SimpleNamespace
from typing import List, Tuple


def trace_collector(**kwargs) -> object:
    """
    Todo:  Insert docstring.

    Parameters:
        **kwargs:

    Returns:
        Todo:  Figure this out.
    """
    trace_name = kwargs["trace"]
    collectors = [c for c in Trace.subclasses if c.trace_name == trace_name]
    if len(collectors) == 1:
        collector = collectors[0]
        return collector(**kwargs)
    elif len(collectors) == 0:
        raise RuntimeError(f"Unsupported trace type:  {trace_name}")
    else:
        raise RuntimeError(f"Multiple trace types match '{trace_name}'.")


def stats_collectors(**kwargs) -> List[object]:
    """
    Todo:  Insert docstring.

    Parameters:
        **kwargs:

    Returns:
        Todo:  Figure this out.
    """
    collectors = []
    if "measure" in kwargs:
        interval = kwargs["interval"] if "interval" in kwargs else 1.0
        manager = Manager()
        for collector in StatsCollector.subclasses:
            if collector.stat_name in kwargs["measure"]:
                collectors.append(collector(interval, manager))
    return collectors


class Shell:
    """
    Todo:  Insert docstring.
    """

    def __init__(self, pwd: Path = Path.cwd()) -> None:
        """
        Initialize a :class:`Shell` object.

        Parameters:
            pwd:  The directory to change to when starting the
                :class:`Shell`.
        """
        self.aux_stdin_rfd, self.aux_stdin_wfd = os.pipe()
        self.aux_stdout_rfd, self.aux_stdout_wfd = os.pipe()
        self.aux_stderr_rfd, self.aux_stderr_wfd = os.pipe()

        # Todo:  What's happening here?
        aux_stdout_write_flags = fcntl.fcntl(self.aux_stdout_wfd,
                                             fcntl.F_GETFL)
        fcntl.fcntl(self.aux_stdout_wfd,
                    fcntl.F_SETFL,
                    aux_stdout_write_flags | os.O_NONBLOCK)
        aux_stderr_write_flags = fcntl.fcntl(self.aux_stderr_wfd,
                                             fcntl.F_GETFL)
        fcntl.fcntl(self.aux_stderr_wfd,
                    fcntl.F_SETFL,
                    aux_stderr_write_flags | os.O_NONBLOCK)

        # Todo:  What's happening here?
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

    def __del__(self) -> None:
        """
        Close all the open file descriptors.
        """
        for fd in [self.aux_stdin_rfd, self.aux_stdin_wfd,
                   self.aux_stdout_rfd, self.aux_stdout_wfd,
                   self.aux_stderr_rfd, self.aux_stderr_wfd]:
            try:
                os.close(fd)
            except OSError as e:
                if "Bad file descriptor" not in e.strerror:
                    raise e

    def __eq__(self, other: Shell) -> bool:
        """
        Determine if this :class:`Shell` object is equal to another one.

        Parameters:
            other:  The other :class:`Shell` to compare against.

        Returns:
            ``True`` if the types and working directories of the two
            objects are equal; ``False`` otherwise.
        """
        return type(self) == type(other) and self.pwd() == other.pwd()

    def pwd(self) -> str:
        """
        Get the current working directory.

        Returns:
            The current working directory.
        """
        directory, _ = self.auxiliary_command(posix="pwd", nt="cd", strip=True)
        return directory

    def cd(self, path: Path) -> None:
        """
        Change to the given directory.

        Parameters:
            path:  The directory to change to.

        Todo:  Figure out if ``path`` is a ``str`` or ``Path``.
        """
        os.chdir(path)
        self.auxiliary_command(posix=f"cd {path}", nt=f"cd {path}")

    def run(self, command: str, **kwargs) -> SimpleNamespace:
        """
        Todo:  Insert docstring.

        Parameters:
            command:  The command to run in the :class:`Shell`.
            **kwargs:

        Returns:
            Todo:  Figure this out.
        """
        start = round(time() * 1000)

        # Todo:  Why are the enclosing braces necessary?
        if kwargs.get("devnull_stdin"):
            os.write(self.aux_stdin_wfd,
                     f"{{\n{command}\n}} </dev/null\n".encode())
        else:
            os.write(self.aux_stdin_wfd, f"{{\n{command}\n}}\n".encode())

        # Todo:  What are these next three lines doing?
        os.write(self.aux_stdin_wfd, f"RET_CODE=$?\n".encode())
        os.write(self.aux_stdin_wfd, f"printf '\\4'\n".encode())
        os.write(self.aux_stdin_wfd, f"printf '\\4' 1>&2\n".encode())
        try:
            output = self.tee(self.shell.stdout, self.shell.stderr, **kwargs)
        except KeyboardInterrupt:
            os.close(self.aux_stdin_wfd)

            # Todo:  Should this error message be changed?
            raise RuntimeError(
                f"There was a problem running the command `{command}`.  "
                "This is a fatal error and we cannot continue.  Ensure that "
                "the syntax of the command is correct."
            )
        finish = round(time() * 1000)

        # Todo:  Why is there no `nt="foo"`?
        aux_out, _ = self.auxiliary_command(posix="echo $RET_CODE")
        try:
            returncode = int(aux_out)
        except ValueError:
            returncode = "N/A"
        return SimpleNamespace(
            returncode=returncode,
            args=command,
            stdout=output.stdout_str,
            stderr=output.stderr_str,
            start=start,
            finish=finish,
            wall=finish - start
        )

    @staticmethod
    def tee(stdout, stderr, **kwargs) -> SimpleNamespace:
        """
        Todo:  Insert docstring.

        Parameters:
            stdout:
            stderr:
            **kwargs:

        Todo:  Figure out the types of the inputs.

        Returns:
            Todo:  Figure this out.
        """
        sys_stdout = None if kwargs.get("quiet_stdout") else sys.stdout
        sys_stderr = None if kwargs.get("quiet_stderr") else sys.stderr
        stdout_io = StringIO() if kwargs.get("stdout_str") else None
        stderr_io = StringIO() if kwargs.get("stderr_str") else None
        stdout_path = open(kwargs.get("stdout_path", os.devnull), "a")
        stderr_path = open(kwargs.get("stderr_path", os.devnull), "a")
        stdout_tee = [sys_stdout, stdout_io, stdout_path]
        stderr_tee = [sys_stderr, stderr_io, stderr_path]

        def write(input_file, output_files) -> None:
            """
            Todo:  Insert docstring.

            Parameters:
                input_file:
                output_files:

            Todo:  Determine types for inputs.
            """
            chunk = os.read(input_file.fileno(), 4096)
            while chunk and chunk[-1] != 4:
                for output_file in output_files:
                    if output_file is not None:
                        output_file.write(chunk.decode(errors="ignore"))
                chunk = os.read(input_file.fileno(), 4096)
            if not chunk:
                _thread.interrupt_main()
            chunk = chunk[:-1]
            for output_file in output_files:
                if output_file is not None:
                    output_file.write(chunk.decode(errors="ignore"))

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
            if (file not in [None, sys.stdout, sys.stderr, sys.stdin]
                    and not file.closed):
                file.close()
        return SimpleNamespace(
            stdout_str=stdout_str,
            stderr_str=stderr_str
        )

    def auxiliary_command(self, **kwargs) -> Tuple[str, str]:
        """
        Todo:  Insert docstring.

        Parameters:
            **kwargs:

        Returns:
            Todo:  Figure this out.
        """
        stdout, stderr = None, None

        # Todo:  Should these lines be inside the `if` below?
        cmd = kwargs[os.name]
        out = self.aux_stdout_wfd
        err = self.aux_stderr_wfd
        if os.name in kwargs:
            os.write(self.aux_stdin_wfd, f"{cmd} 1>&{out} 2>&{err}\n".encode())
            os.write(self.aux_stdin_wfd, f"printf '\\4' 1>&{out}\n".encode())
            os.write(self.aux_stdin_wfd, f"printf '\\4' 1>&{err}\n".encode())
            stdout = ""
            stderr = ""

            # Todo:  What's with the magic numbers?
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
            if kwargs.get("strip"):
                if stdout:
                    stdout = stdout.strip()
                if stderr:
                    stderr = stderr.strip()
        return stdout, stderr


class Trace:
    """
    Todo:  Insert docstring.
    """
    trace_name = "undefined"
    subclasses = []

    def subclass(TraceSubclass):
        """
        Todo:  Insert docstring.
        """
        if issubclass(TraceSubclass, Trace):
            Trace.subclasses.append(TraceSubclass)
        return TraceSubclass

    def __init__(self, **kwargs):
        """
        Todo:  Insert docstring.
        """
        if kwargs.get("trace_path"):
            self.output_path = Path(kwargs["trace_path"])
        else:
            self.output_path = Path(f"{self.trace_name}.log")

    @property
    @abstractmethod
    def trace_args(self):
        """
        Todo:  Insert docstring.
        """
        raise AbstractMethod()

    def command(self, command, **kwargs):
        """
        Todo:  Insert docstring.
        """
        return f"{self.trace_args} -- {command}"


class StatsCollector:
    """
    Todo:  Insert docstring.
    """
    stat_name = "undefined"
    subclasses = []

    def subclass(StatsCollectorSubclass):
        """
        Todo:  Insert docstring.
        """
        if issubclass(StatsCollectorSubclass, StatsCollector):
            StatsCollector.subclasses.append(StatsCollectorSubclass)
        return StatsCollectorSubclass

    def __init__(self, interval, manager):
        """
        Todo:  Insert docstring.
        """
        self.interval = interval
        self.process = Process(target=self.loop, args=())

    def start(self):
        """
        Todo:  Insert docstring.
        """
        self.process.start()

    def loop(self):
        """
        Todo:  Insert docstring.
        """
        while True:
            self.collect()
            sleep(self.interval)

    @abstractmethod
    def collect(self):
        """
        Todo:  Insert docstring.
        """
        raise AbstractMethod()

    @abstractmethod
    def unproxied_stats(self):
        """
        Todo:  Insert docstring.
        """
        raise AbstractMethod()

    def finish(self):
        """
        Todo:  Insert docstring.
        """
        self.process.terminate()
        return self.unproxied_stats()


class FileAlreadyExists(RuntimeError):
    def __init__(self, file):
        """
        Todo:  Insert docstring.
        """
        super().__init__(f"{file.resolve()} already exists! "
                         "Delete or rename and try rerunning this.")


class AbstractMethod(NotImplementedError):
    def __init__(self):
        """
        Todo:  Insert docstring.
        """
        class_name = (
            inspect.stack()[1].frame.f_locals['self'].__class__.__name__
        )
        method_name = inspect.stack()[1].function
        super().__init__(f"{class_name} must implement {method_name}()")
