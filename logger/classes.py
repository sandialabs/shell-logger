#!/usr/bin/env python3
from .util import run_teed_command, program_exists_in_path
from abc import abstractmethod
from collections import namedtuple
import inspect
from multiprocessing import Process, Manager
from pathlib import Path
import time

def trace_collector(command, **kwargs):
    trace_name = kwargs["trace"]
    Collectors = [c for c in Trace.subclasses if c.trace_name == trace_name]
    if len(Collectors) == 1:
        Collector = Collectors[0]
        return Collector(command, **kwargs)
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

Stat = namedtuple("Stat", ["data", "svg"])

class Trace:
    trace_name = "undefined"
    subclasses = []
    def subclass(TraceSubclass):
        if (issubclass(TraceSubclass, Trace)):
            Trace.subclasses.append(TraceSubclass)
        return TraceSubclass
    def __init__(self, command, **kwargs):
        program_exists_in_path(self.trace_name)
        if kwargs.get("trace_path"):
            self.output_path = Path(kwargs["trace_path"])
        else:
            self.output_path = Path(f"{self.trace_name}.log")
        self.command = command
    @property
    @abstractmethod
    def trace_args(self):
        raise AbstractMethod()
    def __call__(self, **kwargs):
        command = f"{self.trace_args} -- {self.command}"
        completed_process = run_teed_command(command, **kwargs)
        return completed_process

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

