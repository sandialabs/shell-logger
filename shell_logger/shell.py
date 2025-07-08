"""Provides the :class:`Shell` class."""

# © 2023 National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the
# U.S. Government retains certain rights in this software.

# SPDX-License-Identifier: BSD-3-Clause

from __future__ import annotations

import _thread
import fcntl
import os
import subprocess
import sys
from io import StringIO
from pathlib import Path
from threading import Thread
from time import time
from types import SimpleNamespace
from typing import IO, Optional, TextIO

END_OF_READ = 4


class Shell:  # noqa: PLW1641
    """
    Manage interactions with the underlying shell.

    Spawns a shell subprocess that inherits five unnamed pipes
    (``stdout``, ``stderr``, ``stdin``, ``aux_stdout``, ``aux_stderr``).

    Attributes:
        login_shell (bool):  Whether or not the spawned shell should be
            a login shell.
        aux_stdin_rfd (int):  The read file descriptor for ``stdin``.
        aux_stdin_wfd (int):  The write file descriptor for ``stdin``.
        aux_stdout_rfd (int):  The read file descriptor for ``stdout``.
        aux_stdout_wfd (int):  The write file descriptor for ``stdout``.
        aux_stderr_rfd (int):  The read file descriptor for ``stderr``.
        aux_stderr_wfd (int):  The write file descriptor for ``stderr``.
        shell_subprocess (Popen[str]):  The subprocess for interacting
            with the shell.
    """

    def __init__(
        self, pwd: Optional[Path] = None, *, login_shell: bool = False
    ) -> None:
        """
        Initialize a :class:`Shell` object.

        Parameters:
            pwd:  The directory to change to when starting the
                :class:`Shell`.
            login_shell:  Whether or not the spawned shell should be a
                login shell.
        """
        self.login_shell = login_shell

        # Corresponds to the 0, 1, and 2 file descriptors of the shell
        # we're going to spawn.
        self.aux_stdin_rfd, self.aux_stdin_wfd = os.pipe()
        self.aux_stdout_rfd, self.aux_stdout_wfd = os.pipe()
        self.aux_stderr_rfd, self.aux_stderr_wfd = os.pipe()

        # Get the current flags of the file descriptors.
        aux_stdout_write_flags = fcntl.fcntl(
            self.aux_stdout_wfd, fcntl.F_GETFL
        )
        aux_stderr_write_flags = fcntl.fcntl(
            self.aux_stderr_wfd, fcntl.F_GETFL
        )

        # Make writes non-blocking.
        fcntl.fcntl(
            self.aux_stdout_wfd,
            fcntl.F_SETFL,
            aux_stdout_write_flags | os.O_NONBLOCK,
        )
        fcntl.fcntl(
            self.aux_stderr_wfd,
            fcntl.F_SETFL,
            aux_stderr_write_flags | os.O_NONBLOCK,
        )

        # Ensure the file descriptors are inheritable by the shell
        # subprocess.
        os.set_inheritable(self.aux_stdout_wfd, True)
        os.set_inheritable(self.aux_stderr_wfd, True)
        shell_command = [os.environ.get("SHELL") or "/bin/sh"]
        if self.login_shell:
            shell_command.append("-l")
        self.shell_subprocess = subprocess.Popen(
            shell_command,
            stdin=self.aux_stdin_rfd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            close_fds=False,
        )
        os.set_inheritable(self.aux_stdout_wfd, False)
        os.set_inheritable(self.aux_stderr_wfd, False)

        # Start the shell in the given directory.
        if pwd is None:
            pwd = Path.cwd()
        self.cd(pwd)

    def __del__(self) -> None:
        """Close all the open file descriptors."""
        for fd in [
            self.aux_stdin_rfd,
            self.aux_stdin_wfd,
            self.aux_stdout_rfd,
            self.aux_stdout_wfd,
            self.aux_stderr_rfd,
            self.aux_stderr_wfd,
        ]:
            try:
                os.close(fd)
            except OSError as e:  # noqa: PERF203
                if "Bad file descriptor" not in e.strerror:
                    raise

    def __eq__(self, other: Shell) -> bool:
        """
        Determine if this :class:`Shell` object is equal to another one.

        Parameters:
            other:  The other :class:`Shell` to compare against.

        Returns:
            ``True`` if the types and working directories of the two
            objects are equal; ``False`` otherwise.
        """
        return isinstance(self, type(other)) and self.pwd() == other.pwd()

    def pwd(self) -> str:
        """
        Get the current working directory.

        Returns:
            The current working directory.
        """
        directory, _ = self.auxiliary_command(posix="pwd", strip=True)
        return directory

    def cd(self, path: Path) -> None:
        """
        Change to the given directory.

        Parameters:
            path:  The directory to change to.
        """
        os.chdir(path)
        self.auxiliary_command(posix=f"cd {path}")

    def run(self, command: str, **kwargs) -> SimpleNamespace:
        """
        Run a command in the underlying shell.

        Write a ``command`` to the :class:`Shell` class' shell
        subprocess' ``stdin``, and pull the ``stdout`` and ``stderr``.

        Parameters:
            command:  The command to run in the shell subprocess.
            **kwargs:  Any additional arguments to pass to :func:`tee`.

        Returns:
            The command run, along with its return code, ``stdout``,
            ``stderr``, start/stop time, and duration.
        """
        milliseconds_per_second = 10**3
        start = round(time() * milliseconds_per_second)

        # Wrap the `command` in {braces} to support newlines and
        # heredocs to tell the shell "this is one giant statement".
        # Then run the command.
        if kwargs.get("devnull_stdin"):
            os.write(
                self.aux_stdin_wfd, f"{{\n{command}\n}} </dev/null\n".encode()
            )
        else:
            os.write(self.aux_stdin_wfd, f"{{\n{command}\n}}\n".encode())

        # Set the `RET_CODE` environment variable, such that we can
        # access it later.
        os.write(self.aux_stdin_wfd, b"RET_CODE=$?\n")

        # Because these writes are non-blocking, tell the shell that the
        # writes are complete.
        os.write(self.aux_stdin_wfd, b"printf '\\4'\n")
        os.write(self.aux_stdin_wfd, b"printf '\\4' 1>&2\n")

        # Tee the output to multiple sinks (files, strings,
        # `stdout`/`stderr`).
        try:
            output = self.tee(
                self.shell_subprocess.stdout,
                self.shell_subprocess.stderr,
                **kwargs,
            )

        # Note:  If something goes wrong in `tee()`, the only way to reliably
        # propagate an exception from a thread that's spawned is to raise a
        # KeyboardInterrupt.
        except KeyboardInterrupt:
            os.close(self.aux_stdin_wfd)
            message = (
                f"There was a problem running the command `{command}`.  "
                "This is a fatal error and we cannot continue.  Ensure that "
                "the syntax of the command is correct."
            )
            raise RuntimeError(message) from None
        finish = round(time() * milliseconds_per_second)

        # Pull the return code and return the results.  Note that if the
        # command executed spawns a sub-shell, you won't really have a
        # return code.
        aux_out, _ = self.auxiliary_command(posix="echo $RET_CODE")
        try:
            return_code = int(aux_out)
        except ValueError:
            return_code = "N/A"
        return SimpleNamespace(
            returncode=return_code,
            args=command,
            stdout=output.stdout_str,
            stderr=output.stderr_str,
            start=start,
            finish=finish,
            wall=finish - start,
        )

    @staticmethod
    def tee(  # noqa: C901
        stdout: Optional[IO[bytes]], stderr: Optional[IO[bytes]], **kwargs
    ) -> SimpleNamespace:
        """
        Write output/error streams to multiple files.

        Split ``stdout`` and ``stderr`` file objects to write to
        multiple files.

        Parameters:
            stdout:  The ``stdout`` file object to be split.
            stderr:  The ``stderr`` file object to be split.
            **kwargs:  Additional arguments.

        Returns:
            The ``stdout`` and ``stderr`` as strings.

        Todo:
          * Replace ``**kwargs`` with function arguments.
        """
        sys_stdout = None if kwargs.get("quiet_stdout") else sys.stdout
        sys_stderr = None if kwargs.get("quiet_stderr") else sys.stderr
        stdout_io = StringIO() if kwargs.get("stdout_str") else None
        stderr_io = StringIO() if kwargs.get("stderr_str") else None
        stdout_path = kwargs.get("stdout_path", Path(os.devnull)).open("a")
        stderr_path = kwargs.get("stderr_path", Path(os.devnull)).open("a")
        stdout_tee = [sys_stdout, stdout_io, stdout_path]
        stderr_tee = [sys_stderr, stderr_io, stderr_path]

        def write(input_file: TextIO, output_files: list[TextIO]) -> None:
            """
            Write an input to multiple outputs.

            Take the data from an input file object and write it to
            multiple output file objects.

            Parameters:
                input_file:  The file object from which to read.
                output_files:  A list of file objects to write to.
            """
            # Read chunks from the input file.
            chunk_size = 4096  # 4 KB
            chunk = os.read(input_file.fileno(), chunk_size)
            while chunk and chunk[-1] != END_OF_READ:
                for output_file in output_files:
                    if output_file is not None:
                        output_file.write(chunk.decode(errors="ignore"))
                chunk = os.read(input_file.fileno(), chunk_size)

            # If something goes wrong in the `tee()`, the only way to
            # reliably propagate an exception from a thread that's
            # spawned is to raise a KeyboardInterrupt.
            if not chunk:
                _thread.interrupt_main()

            # Remove the end-of-transmission character, and write the
            # last chunk.
            chunk = chunk[:-1]
            for output_file in output_files:
                if output_file is not None:
                    output_file.write(chunk.decode(errors="ignore"))

        # Spawn threads to write to `stdout` and `stderr`.
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

        # Close any open file descriptors and return the `stdout` and
        # `stderr`.
        for file in stdout_tee + stderr_tee:
            if (
                file not in [None, sys.stdout, sys.stderr, sys.stdin]
                and not file.closed
            ):
                file.close()
        return SimpleNamespace(stdout_str=stdout_str, stderr_str=stderr_str)

    def auxiliary_command(
        self, **kwargs
    ) -> tuple[Optional[str], Optional[str]]:
        """
        Run auxiliary commands like `umask`, `pwd`, `env`, etc.

        Parameters:
            **kwargs:  Additional arguments.

        Note:  This is effectively the same as :func:`run`, but:
            1. The ``stdout`` and ``stderr`` get redirected to the
               auxiliary file descriptors.
            2. You don't tee the ``stdout`` or ``stderr``.

        Todo:
          * Maybe combine this with :func:`run` with extra flags.
          * Replace ``**kwargs`` with function arguments.

        Returns:
            The ``stdout`` and ``stderr`` of the command run.
        """
        stdout, stderr = None, None
        out = self.aux_stdout_wfd
        err = self.aux_stderr_wfd
        if os.name in kwargs:
            cmd = kwargs[os.name]
            os.write(self.aux_stdin_wfd, f"{cmd} 1>&{out} 2>&{err}\n".encode())
            os.write(self.aux_stdin_wfd, f"printf '\\4' 1>&{out}\n".encode())
            os.write(self.aux_stdin_wfd, f"printf '\\4' 1>&{err}\n".encode())
            stdout = ""
            stderr = ""

            max_anonymous_pipe_buffer_size = 65536
            aux = os.read(self.aux_stdout_rfd, max_anonymous_pipe_buffer_size)
            while aux[-1] != END_OF_READ:
                stdout += aux.decode()
                aux = os.read(
                    self.aux_stdout_rfd, max_anonymous_pipe_buffer_size
                )
            aux = aux[:-1]
            stdout += aux.decode()
            aux = os.read(self.aux_stderr_rfd, max_anonymous_pipe_buffer_size)
            while aux[-1] != END_OF_READ:
                stderr += aux.decode()
                aux = os.read(
                    self.aux_stderr_rfd, max_anonymous_pipe_buffer_size
                )
            aux = aux[:-1]
            stderr += aux.decode()
            if kwargs.get("strip"):
                if stdout:
                    stdout = stdout.strip()
                if stderr:
                    stderr = stderr.strip()
        return stdout, stderr
