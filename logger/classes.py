#!/usr/bin/env python3
from .util import runCommandWithConsole, checkIfProgramExistsInPath
from abc import abstractmethod
from collections import namedtuple
from inspect import stack
from multiprocessing import Process, Manager
from pathlib import Path
from subprocess import run
from time import sleep

def traceCollector(command, **kwargs):
    traceName = kwargs["trace"]
    Collectors = [c for c in Trace.subclasses if c.traceName == traceName]
    if len(Collectors) == 1:
        Collector = Collectors[0]
        return Collector(command, **kwargs)
    elif len(Collectors) == 0:
        raise RuntimeError(f"Unsupported trace type: {traceName}")
    else:
        raise RuntimeError(f"Multiple trace types match {traceName}")

def statsCollectors(**kwargs):
    collectors = []
    if "measure" in kwargs:
        interval = kwargs["interval"] if "interval" in kwargs else 1.0
        stats = {}
        manager = Manager()
        for Collector in StatsCollector.subclasses:
            if Collector.statName in kwargs["measure"]:
                collectors.append(Collector(interval, manager))
    return collectors

TraceResult = namedtuple("TraceResult", ["traceOutput", "completedProcess"])

Stat = namedtuple("Stat", ["data", "svg"])

class Trace:
    traceName = "undefined"
    subclasses = []
    def subclass(TraceSubclass):
        if (issubclass(TraceSubclass, Trace)):
            Trace.subclasses.append(TraceSubclass)
        return TraceSubclass
    def __init__(self, command):
        checkIfProgramExistsInPath(self.traceName)
        self.outputPath = Path(f"{self.traceName}.log")
        self.command = command
    @property
    @abstractmethod
    def traceArgs(self):
        raise AbstractMethod()
    def __call__(self):
        traceOutput = None
        if self.outputPath.exists():
            raise FileAlreadyExists(self.outputPath)
        try:
            command = f"{self.traceArgs} -- {self.command}"
            completedProcess = runCommandWithConsole(command)
            with open(self.outputPath) as traceFile:
                traceOutput = traceFile.read()
        finally:
            if self.outputPath.exists():
                self.outputPath.unlink()
        return TraceResult(traceOutput, completedProcess)

class StatsCollector:
    statName = "undefined"
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
            sleep(self.interval)
    @abstractmethod
    def collect(self):
        raise AbstractMethod()
    @abstractmethod
    def unproxiedStats(self):
        raise AbstractMethod()
    def finish(self):
        self.process.terminate()
        return self.unproxiedStats()

class FileAlreadyExists(RuntimeError):
    def __init__(self, file):
        super().__init__(f"{file.resolve()} already exists! "
                          "Delete or rename and try rerunning this.")

class AbstractMethod(NotImplementedError):
    def __init__(self):
        className = stack()[1].frame.f_locals['self'].__class__.__name__
        methodName = stack()[1].function
        super().__init__(f"{className} must implement {methodName}()")

