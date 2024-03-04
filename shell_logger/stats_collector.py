#!/usr/bin/env python3
"""
Provides the various means of collecting machine statistics.
"""

# © 2024 National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the
# U.S. Government retains certain rights in this software.

# SPDX-License-Identifier: BSD-3-Clause

from __future__ import annotations
from .abstract_method import AbstractMethod
from abc import abstractmethod
from multiprocessing import Process
from multiprocessing.managers import SyncManager
from multiprocessing import Manager
import os
from pathlib import Path
from time import sleep, time
from typing import List, Tuple

try:
    import psutil
except ModuleNotFoundError:
    psutil = None


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


if psutil is not None:

    @StatsCollector.subclass
    class DiskStatsCollector(StatsCollector):
        """
        A means of running commands while collecting disk usage
        statistics.
        """

        stat_name = "disk"

        def __init__(self, interval: float, manager: SyncManager) -> None:
            """
            Initialize the :class:`DiskStatsCollector` object.

            Parameters:
                interval:  How many seconds to sleep between polling.
                manager:  The multiprocessing manager used to control
                    the process used to collect the statistics.
            """
            super().__init__(interval, manager)
            self.stats = manager.dict()
            self.mount_points = [
                p.mountpoint for p in psutil.disk_partitions()
            ]
            for location in [
                "/tmp",
                "/dev/shm",
                f"/var/run/user/{os.getuid()}",
            ]:
                if (
                    location not in self.mount_points
                    and Path(location).exists()
                ):
                    self.mount_points.append(location)
            for m in self.mount_points:
                self.stats[m] = manager.list()

        def collect(self) -> None:
            """
            Poll the disks to determine how much free space they have.
            """
            milliseconds_per_second = 10**3
            timestamp = round(time() * milliseconds_per_second)
            for m in self.mount_points:
                self.stats[m].append((timestamp, psutil.disk_usage(m).percent))

        def unproxied_stats(self) -> dict:
            """
            Translate the statistics from the multiprocessing
            ``SyncManager`` 's data structure to a ``dict``.

            Returns:
                A mapping from the disk mount points to tuples of
                timestamps and percent of disk space free.
            """
            return {k: list(v) for k, v in self.stats.items()}

    @StatsCollector.subclass
    class CPUStatsCollector(StatsCollector):
        """
        A means of running commands while collecting CPU usage
        statistics.
        """

        stat_name = "cpu"

        def __init__(self, interval: float, manager: SyncManager) -> None:
            """
            Initialize the :class:`CPUStatsCollector` object.

            Parameters:
                interval:  How many seconds to sleep between polling.
                manager:  The multiprocessing manager used to control
                    the process used to collect the statistics.
            """
            super().__init__(interval, manager)
            self.stats = manager.list()

        def collect(self) -> None:
            """
            Determine how heavily utilized the CPU is at the moment.
            """
            milliseconds_per_second = 10**3
            timestamp = round(time() * milliseconds_per_second)
            self.stats.append((timestamp, psutil.cpu_percent(interval=None)))

        def unproxied_stats(self) -> List[Tuple[float, float]]:
            """
            Translate the statistics from the multiprocessing
            ``SyncManager`` 's data structure to a ``list``.

            Returns:
                A list of (timestamp, % CPU used) data points.
            """
            return list(self.stats)

    @StatsCollector.subclass
    class MemoryStatsCollector(StatsCollector):
        """
        A means of running commands while collecting memory usage
        statistics.
        """

        stat_name = "memory"

        def __init__(self, interval: float, manager: SyncManager) -> None:
            """
            Initialize the :class:`MemoryStatsCollector` object.

            Parameters:
                interval:  How many seconds to sleep between polling.
                manager:  The multiprocessing manager used to control
                    the process used to collect the statistics.
            """
            super().__init__(interval, manager)
            self.stats = manager.list()

        def collect(self) -> None:
            """
            Determine how much memory is currently being used.
            """
            milliseconds_per_second = 10**3
            timestamp = round(time() * milliseconds_per_second)
            self.stats.append((timestamp, psutil.virtual_memory().percent))

        def unproxied_stats(self) -> List[Tuple[float, float]]:
            """
            Translate the statistics from the multiprocessing
            ``SyncManager`` 's data structure to a ``list``.

            Returns:
                A list of (timestamp, % memory used) data points.
            """
            return list(self.stats)


# If we don't have `psutil`, return null objects.
else:

    @StatsCollector.subclass
    class DiskStatsCollector(StatsCollector):
        """
        A phony :class:`DiskStatsCollector` used when ``psutil`` is
        unavailable.  This collects no disk statistics.
        """

        stat_name = "disk"

        def __init__(self, interval: float, manager: SyncManager) -> None:
            """
            Initialize the object via the parent's constructor.

            Parameters:
                interval:  How many seconds to sleep between polling.
                manager:  The multiprocessing manager used to control
                    the process used to collect the statistics.
            """
            super().__init__(interval, manager)

        def collect(self) -> None:
            """
            Don't collect any disk statistics.
            """
            pass

        def unproxied_stats(self) -> None:
            """
            If asked for the disk statistics, don't provide any.

            Returns:
                None
            """
            return None

    @StatsCollector.subclass
    class CPUStatsCollector(StatsCollector):
        """
        A phony :class:`CPUStatsCollector` used when ``psutil`` is
        unavailable.  This collects no CPU statistics.
        """

        stat_name = "cpu"

        def __init__(self, interval: float, manager: SyncManager) -> None:
            """
            Initialize the object via the parent's constructor.

            Parameters:
                interval:  How many seconds to sleep between polling.
                manager:  The multiprocessing manager used to control
                    the process used to collect the statistics.
            """
            super().__init__(interval, manager)

        def collect(self) -> None:
            """
            Don't collect any CPU statistics.
            """
            pass

        def unproxied_stats(self) -> None:
            """
            If asked for CPU statistics, don't provide any.

            Returns:
                None
            """
            return None

    @StatsCollector.subclass
    class MemoryStatsCollector(StatsCollector):
        """
        A phony :class:`MemoryStatsCollector` used when ``psutil`` is
        unavailable.  This collects no memory statistics.
        """

        stat_name = "memory"

        def __init__(self, interval: float, manager: SyncManager) -> None:
            """
            Initialize the object via the parent's constructor.

            Parameters:
                interval:  How many seconds to sleep between polling.
                manager:  The multiprocessing manager used to control
                    the process used to collect the statistics.
            """
            super().__init__(interval, manager)

        def collect(self) -> None:
            """
            Don't collect any memory statistics.
            """
            pass

        def unproxied_stats(self) -> None:
            """
            If asked for memory statistics, don't provide any.

            Returns:
                None
            """
            return None
