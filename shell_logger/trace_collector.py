"""Provides the means of collecting various trace data."""

# © 2023 National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the
# U.S. Government retains certain rights in this software.

# SPDX-License-Identifier: BSD-3-Clause

from __future__ import annotations

from abc import abstractmethod
from pathlib import Path


def trace_collector(**kwargs) -> TraceCollector:
    """
    Generate trace collectors.

    A factory method that returns any subclass of
    :class:`TraceCollector` that has the ``@TraceCollector.subclass``
    decorator applied to it.

    Parameters:
        **kwargs:  Any supported arguments of the
            :class:`TraceCollector` subclass.

    Returns:
        A single instance of a :class:`TraceCollector` subclass.
    """
    trace_name = kwargs["trace"]
    collectors = [
        c for c in TraceCollector.subclasses if c.trace_name == trace_name
    ]
    if len(collectors) == 1:
        collector = collectors[0]
        return collector(**kwargs)
    if len(collectors) == 0:
        message = f"Unsupported trace type:  {trace_name}"
        raise RuntimeError(message)
    message = f"Multiple trace types match '{trace_name}'."
    raise RuntimeError(message)


class TraceCollector:
    """
    Trace a command run in the underlying shell.

    Provides an interface for the :class:`ShellLogger` to run commands
    with a certain trace (e.g., ``strace`` or ``ltrace``).
    """

    trace_name = "undefined"  # Should be defined by subclasses.
    subclasses = []  # noqa: RUF012

    @staticmethod
    def subclass(trace_subclass: type):
        """
        Mark a class as being a supported trace collector.

        This is a class decorator that adds to a list of supported
        :class:`TraceCollector` classes for the :func:`trace_collector`
        factory method.
        """
        if issubclass(trace_subclass, TraceCollector):
            TraceCollector.subclasses.append(trace_subclass)
        return trace_subclass

    def __init__(self, **kwargs):
        """
        Initialize the :class:`TraceCollector` object.

        Set up the output file where the trace information will be
        written.
        """
        if kwargs.get("trace_path"):
            self.output_path = Path(kwargs["trace_path"])
        else:
            self.output_path = Path(f"{self.trace_name}.log")

    @property
    @abstractmethod
    def trace_args(self) -> str:
        """
        Get the trace command.

        The trace command and the arguments you pass to it, but not the
        command you're tracing.  E.g., return `strace -f -c -e "open"`.
        """

    def command(self, command: str):
        """
        Get the command to be run in the underlying shell.

        Return a command that runs a trace on ``command``.  E.g., ``ls
        -l`` might get translated to ``strace -f -c -e 'open' -- ls
        -l``.

        Parameters:
            command:  The command to be traced.
        """
        return f"{self.trace_args} -- {command}"


@TraceCollector.subclass
class STraceCollector(TraceCollector):
    """
    Run ``strace`` on commands.

    An interface between :class:`ShellLogger` and the ``strace``
    command.
    """

    trace_name = "strace"

    def __init__(self, **kwargs) -> None:
        """Initialize the :class:`STraceCollector` instance."""
        super().__init__(**kwargs)
        self.summary = bool(kwargs.get("summary"))
        self.expression = kwargs.get("expression")

    @property
    def trace_args(self) -> str:
        """Wraps a command in a ``strace`` command."""
        args = f"strace -f -o {self.output_path}"
        if self.summary:
            args += " -c"
        if self.expression:
            args += f" -e '{self.expression}'"
        return args


@TraceCollector.subclass
class LTraceCollector(TraceCollector):
    """
    Run ``ltrace`` on commands.

    An interface between :class:`ShellLogger` and the ``ltrace``
    command.
    """

    trace_name = "ltrace"

    def __init__(self, **kwargs):
        """Initialize the :class:`LTraceCollector` instance."""
        super().__init__(**kwargs)
        self.summary = bool(kwargs.get("summary"))
        self.expression = kwargs.get("expression")

    @property
    def trace_args(self):
        """Wraps a command in a ``ltrace`` command."""
        args = f"ltrace -C -f -o {self.output_path}"
        if self.summary:
            args += " -c"
        if self.expression:
            args += f" -e '{self.expression}'"
        return args
