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
from typing import List, TextIO, Tuple


def trace_collector(**kwargs) -> object:
    """
    Todo:  Insert docstring.  Factory.  Returns any subclass of Trace
        that has the @Trace.subclass annotation.

    Parameters:
        **kwargs:  Any supported arguments of the :class:`Trace`
            subclass.

    Returns:
        Todo:  Figure this out.  Single Trace subclass instance.
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
    Todo:  Insert docstring.  See above.

    Parameters:
        **kwargs:

    Returns:
        Todo:  Figure this out.  List[StatsCollector subclasses]
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
    Spawns a shell subprocess that inherits five unnamed pipes (stdout,
    stderr, stdin, aux_stdout, aux_stderr).
    """

    def __init__(self, pwd: Path = Path.cwd()) -> None:
        """
        Initialize a :class:`Shell` object.

        Parameters:
            pwd:  The directory to change to when starting the
                :class:`Shell`.
        """

        # Corresponds to 0,1,2 file descriptors of the shell we're going
        # to spawn.
        self.aux_stdin_rfd, self.aux_stdin_wfd = os.pipe()
        self.aux_stdout_rfd, self.aux_stdout_wfd = os.pipe()
        self.aux_stderr_rfd, self.aux_stderr_wfd = os.pipe()

        # Get the current flags of the file descriptors.
        aux_stdout_write_flags = fcntl.fcntl(self.aux_stdout_wfd,
                                             fcntl.F_GETFL)
        aux_stderr_write_flags = fcntl.fcntl(self.aux_stderr_wfd,
                                             fcntl.F_GETFL)

        # Make writes non-blocking.
        fcntl.fcntl(self.aux_stdout_wfd,
                    fcntl.F_SETFL,
                    aux_stdout_write_flags | os.O_NONBLOCK)
        fcntl.fcntl(self.aux_stderr_wfd,
                    fcntl.F_SETFL,
                    aux_stderr_write_flags | os.O_NONBLOCK)

        # Ensure the file descriptors are inheritable by the shell
        # subprocess.
        os.set_inheritable(self.aux_stdout_wfd, True)
        os.set_inheritable(self.aux_stderr_wfd, True)
        self.shell = subprocess.Popen(os.environ.get("SHELL") or "/bin/sh",
                                      stdin=self.aux_stdin_rfd,
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE,
                                      close_fds=False)
        os.set_inheritable(self.aux_stdout_wfd, False)
        os.set_inheritable(self.aux_stderr_wfd, False)

        # Change to the directory FOOBAR
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
        """
        os.chdir(path)
        self.auxiliary_command(posix=f"cd {path}", nt=f"cd {path}")

    def run(self, command: str, **kwargs) -> SimpleNamespace:
        """
        Write a ``command`` to the :class:`Shell` class' shell
        subprocess' ``stdin``, and pull the ``stdout`` and ``stderr``.

        Parameters:
            command:  The command to run in the shell subprocess.
            **kwargs:

        Returns:
            Todo:  Figure this out.
        """
        start = round(time() * 1000)

        # Wrap the `command` in {braces} to support newlines and
        # heredocs to tell the shell "this is one giant statement".
        # Then run the command.
        if kwargs.get("devnull_stdin"):
            os.write(self.aux_stdin_wfd,
                     f"{{\n{command}\n}} </dev/null\n".encode())
        else:
            os.write(self.aux_stdin_wfd, f"{{\n{command}\n}}\n".encode())

        # Set the `RET_CODE` environment variable, such that we can
        # access it later.
        os.write(self.aux_stdin_wfd, f"RET_CODE=$?\n".encode())

        # Because these writes are non-blocking, tell the shell that the
        # writes are complete.
        os.write(self.aux_stdin_wfd, f"printf '\\4'\n".encode())
        os.write(self.aux_stdin_wfd, f"printf '\\4' 1>&2\n".encode())

        # Tee the output to multiple sinks (files, strings,
        # stdout/stderr).
        try:
            output = self.tee(self.shell.stdout, self.shell.stderr, **kwargs)

        # Note:  If something goes wrong in `tee()`, the only way to reliably
        # propagate an exception from a thread that's spawned is to raise a
        # KeyboardInterrupt.
        except KeyboardInterrupt:
            os.close(self.aux_stdin_wfd)
            raise RuntimeError(
                f"There was a problem running the command `{command}`.  "
                "This is a fatal error and we cannot continue.  Ensure that "
                "the syntax of the command is correct."
            )
        finish = round(time() * 1000)

        # Pull the return code and return the results.  Note that if the
        # command executed spawns a sub-shell, you won't really have a
        # return code.
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
    def tee(
            stdout: TextIO,
            stderr: TextIO,
            **kwargs
    ) -> SimpleNamespace:
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

        def write(input_file: TextIO, output_files: List[TextIO]) -> None:
            """
            Todo:  Insert docstring.

            Parameters:
                input_file:
                output_files:
            """
            chunk_size = 4096  # 4 KB
            chunk = os.read(input_file.fileno(), chunk_size)
            while chunk and chunk[-1] != 4:
                for output_file in output_files:
                    if output_file is not None:
                        output_file.write(chunk.decode(errors="ignore"))
                chunk = os.read(input_file.fileno(), 4096)
            if not chunk:

                # If something goes wrong in the `tee()`, see the note elsewhere.
                _thread.interrupt_main()

            # Remove the EOT character, and write the last chunk.
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
        Todo:  Insert docstring.  The same as the `run` command, but:
            1. stdout/stderr get redirected to the aux fds
            2. you don't tee any out/err

        Purpose is to run aux commands like umask, pwd, env, etc.

        Could maybe combine this with `run` with extra flags.

        Todo:  Rip out Windows support.

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

            magic_number = 65536  # Max amount of info you can write to an unnamed pipe without flushing it.  https://unix.stackexchange.com/questions/343302/anonymous-pipe-kernel-buffer-size
            aux = os.read(self.aux_stdout_rfd, magic_number)
            while aux[-1] != 4:
                stdout += aux.decode()
                aux = os.read(self.aux_stdout_rfd, magic_number)
            aux = aux[:-1]
            stdout += aux.decode()
            aux = os.read(self.aux_stderr_rfd, magic_number)
            while aux[-1] != 4:
                stderr += aux.decode()
                aux = os.read(self.aux_stderr_rfd, magic_number)
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
    Provides an interface for the :class:`ShellLogger` to run commands
    with a certain trace (e.g., ``strace`` or ``ltrace``).
    """
    trace_name = "undefined"  # Should be defined by subclasses.
    subclasses = []

    @staticmethod  # Or is there some @decorator annotation?
    def subclass(tracesubclass: type):
        """
        Todo:  Insert docstring.  Decorator.  Adds to a list of supported Trace classes for the trace_collector factory method.
        """
        if issubclass(tracesubclass, Trace):
            Trace.subclasses.append(tracesubclass)
        return tracesubclass

    def __init__(self, **kwargs):
        """
        Todo:  Insert docstring.
        """

        # Set up the output file where you'll write the trace info.
        if kwargs.get("trace_path"):
            self.output_path = Path(kwargs["trace_path"])
        else:
            self.output_path = Path(f"{self.trace_name}.log")

    @property
    @abstractmethod
    def trace_args(self):
        """
        Todo:  Insert docstring.  The trace command + the arguments you pass to it (but not the command you're tracing).  Needs to be overridden in subclasses.  E.g. return `strace -f -c -e "open"`.
        """
        raise AbstractMethod()

    def command(self, command, **kwargs):
        """
        Return a command that runs a trace on a command.  E.g. "ls -l" -> "strace -f -c -e 'open' -- ls -l"
        """
        return f"{self.trace_args} -- {command}"


class StatsCollector:
    """
    Todo:  Insert docstring.
    """
    stat_name = "undefined"
    subclasses = []

    def subclass(statscollectorsubclass: type):
        """
        Todo:  Insert docstring.
        """
        if issubclass(statscollectorsubclass, StatsCollector):
            StatsCollector.subclasses.append(statscollectorsubclass)
        return statscollectorsubclass

    def __init__(self, interval, manager):
        """
        Todo:  Insert docstring.
        """
        self.interval = interval
        self.process = Process(target=self.loop, args=())

    def start(self):
        """
        Start a subprocess to poll at a certain interval for certain
        statistics.
        """
        self.process.start()

    def loop(self):
        """
        Infinitely loop, collecting stats, until the subprocess is
        terminated.
        """
        while True:
            self.collect()
            sleep(self.interval)

    @abstractmethod
    def collect(self):
        """
        Meant to be overridden.  Called at an interval.  Instantaneous
        collection of a stat.
        """
        raise AbstractMethod()

    @abstractmethod
    def unproxied_stats(self):
        """
        Convert from Python's Manager's datastrcutrues to base Python
        datastructures.
        """
        raise AbstractMethod()

    def finish(self):
        """
        Terminate the infinite loop that's collecting the stats, and
        then return the unproxied stats.
        """
        self.process.terminate()
        return self.unproxied_stats()


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
