#!/usr/bin/env python3

from __future__ import annotations
from abc import abstractmethod
import inspect
from multiprocessing import Process, Manager
from multiprocessing.managers import SyncManager
from pathlib import Path
from time import sleep
from typing import List


def trace_collector(**kwargs) -> Trace:
    """
    A factory method that returns any subclass of :class:`Trace` that
    has the ``@Trace.subclass`` decorator applied to it.

    Parameters:
        **kwargs:  Any supported arguments of the :class:`Trace`
            subclass.

    Returns:
        A single instance of a :class:`Trace` subclass.
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


def stats_collectors(**kwargs) -> List[StatsCollector]:
    """
    A factory method that returns a list of any subclasses of
    :class:`StatsCollector` that have the ``@StatsCollector.subclass``
    decorator applied to them.

    Parameters:
        **kwargs:  Any supported arguments of the
            :class:`StatsCollector` subclasses.

    Returns:
        A collection of instances of :class:`StatsCollector` subclasses.
    """
    collectors = []
    if "measure" in kwargs:
        interval = kwargs["interval"] if "interval" in kwargs else 1.0
        manager = Manager()
        for collector in StatsCollector.subclasses:
            if collector.stat_name in kwargs["measure"]:
                collectors.append(collector(interval, manager))
    return collectors


class Trace:
    """
    Provides an interface for the :class:`ShellLogger` to run commands
    with a certain trace (e.g., ``strace`` or ``ltrace``).
    """
    trace_name = "undefined"  # Should be defined by subclasses.
    subclasses = []

    @staticmethod
    def subclass(trace_subclass: type):
        """
        This is a class decorator that adds to a list of supported
        :class:`Trace` classes for the :func:`trace_collector` factory
        method.
        """
        if issubclass(trace_subclass, Trace):
            Trace.subclasses.append(trace_subclass)
        return trace_subclass

    def __init__(self, **kwargs):
        """
        Initialize the :class:`Trace` object, setting up the output file
        where the trace information will be written.
        """
        if kwargs.get("trace_path"):
            self.output_path = Path(kwargs["trace_path"])
        else:
            self.output_path = Path(f"{self.trace_name}.log")

    @property
    @abstractmethod
    def trace_args(self) -> None:
        """
        The trace command and the arguments you pass to it, but not the
        command you're tracing.  E.g., return `strace -f -c -e "open"`.

        Raises:
            AbstractMethod:  This needs to be overridden by subclasses.
        """
        raise AbstractMethod()

    def command(self, command: str):
        """
        Return a command that runs a trace on ``command``.  E.g., ``ls
        -l`` might get translated to ``strace -f -c -e 'open' -- ls
        -l``.

        Parameters:
            command:  The command to be traced.
        """
        return f"{self.trace_args} -- {command}"


class StatsCollector:
    """
    Provides an interface for the :class:`ShellLogger` to run commands
    while collecting various system statistics.
    """
    stat_name = "undefined"  # Should be defined by subclasses.
    subclasses = []

    @staticmethod
    def subclass(stats_collector_subclass: type):
        """
        This is a class decorator that adds to a list of supported
        :class:`StatsCollector` classes for the :func:`stats_collectors`
        factory method.
        """
        if issubclass(stats_collector_subclass, StatsCollector):
            StatsCollector.subclasses.append(stats_collector_subclass)
        return stats_collector_subclass

    def __init__(self, interval: float, _: SyncManager):
        """
        Initialize the :class:`StatsCollector` object, setting the
        poling interval, and creating the process for collecting the
        statistics.

        Parameters:
            interval:  How long to sleep between collecting statistics.

        Note:
            A ``SyncManager`` will be supplied at the second argument
            for any subclasses.
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
        Infinitely loop, collecting statistics, until the subprocess is
        terminated.
        """
        while True:
            self.collect()
            sleep(self.interval)

    @abstractmethod
    def collect(self):
        """
        Instantaneously collect a statistic.  This is meant to be called
        repeatedly after some time interval.

        Raises:
            AbstractMethod:  This must be overridden by subclasses.
        """
        raise AbstractMethod()

    @abstractmethod
    def unproxied_stats(self):
        """
        Convert from Python's Manager's data structures to base Python
        data structures.

        Raises:
            AbstractMethod:  This must be overridden by subclasses.
        """
        raise AbstractMethod()

    def finish(self):
        """
        Terminate the infinite loop that's collecting the statistics,
        and then return the unproxied statistics.
        """
        self.process.terminate()
        return self.unproxied_stats()


class AbstractMethod(NotImplementedError):
    """
    An ``Exception`` denoting an abstract method that is meant to be
    overridden by a subclass.
    """

    def __init__(self):
        """
        Raise a `NotImplementedError`, indicating which method must be
        implemented for the class to be concrete.
        """
        class_name = (
            inspect.stack()[1].frame.f_locals['self'].__class__.__name__
        )
        method_name = inspect.stack()[1].function
        super().__init__(f"`{class_name}` must implement `{method_name}()`.")
