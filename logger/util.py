#!/usr/bin/env python3
from collections.abc import Iterable, Mapping
from io import StringIO
import itertools
import numpy as np
import matplotlib.pyplot as pyplot
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
import os
import subprocess
import sys
import time
from types import SimpleNamespace

def make_svg_line_chart(data):
    fig, ax = pyplot.subplots(figsize=(6, 2), dpi=80)
    pyplot.plot(*zip(*data))
    pyplot.yticks(np.arange(0, 110, 10))
    ax.xaxis.set_ticks([])
    ax.yaxis.set_major_locator(MultipleLocator(20))
    ax.yaxis.set_major_formatter(FormatStrFormatter('%d%%'))
    ax.yaxis.set_minor_locator(MultipleLocator(10))
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    string_io = StringIO()
    fig.savefig(string_io, format='svg')
    pyplot.close(fig)
    string_io.seek(0)
    lines = string_io.readlines()
    svg = "".join(itertools.dropwhile(lambda line: "<svg" not in line, lines))
    return svg

def nested_SimpleNamespace_to_dict(object):
    if "_asdict" in dir(object):
        return nested_SimpleNamespace_to_dict(object._asdict())
    elif isinstance(object, (str, bytes, tuple)):
        return object
    elif isinstance(object, Mapping):
        return {k:nested_SimpleNamespace_to_dict(v) for k,v in object.items()}
    elif isinstance(object, Iterable):
        return [nested_SimpleNamespace_to_dict(x) for x in object]
    elif isinstance(object, SimpleNamespace):
        return nested_SimpleNamespace_to_dict(object.__dict__)
    else:
        return object

