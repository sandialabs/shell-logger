#!/usr/bin/env python3
from . import resources
from collections.abc import Iterable, Mapping
import importlib.resources
from io import StringIO
import itertools
import numpy as np
import matplotlib.pyplot as pyplot
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
import os
from pathlib import Path
import subprocess
import sys
import time
from types import SimpleNamespace, GeneratorType

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

def opening_html_text():
    return (
        "<!DOCTYPE html>" +
        "<html>" +
        html_header()
    )

def closing_html_text():
    return "</html>"

def append_html(*args, output=Path(os.devnull)):
    with open(output, "a") as file:
        for arg in args:
            if isinstance(arg, GeneratorType):
                for element in arg:
                    file.write(element)
            if isinstance(arg, str):
                file.write(arg)
            if isinstance(arg, bytes):
                file.write(arg.decode())

def html_details(*args, summary=None, indent=0):
    yield ' '*indent + "<details>\n"
    if summary is not None:
        yield ' '*(indent+2) + f"<summary>{summary}</summary>\n"
    for arg in args:
        if isinstance(arg, GeneratorType):
            for element in arg:
                yield element
        if isinstance(arg, str):
            yield arg
        if isinstance(arg, bytes):
            yield arg.decode()
    yield ' '*indent + "</details>\n"

def html_list_item(*args, indent=0, add_br=True):
    if add_br:
        yield ' '*indent + "<li>\n"
    else:
        yield ' '*indent + "<li>"
    for arg in args:
        if isinstance(arg, GeneratorType):
            for element in arg:
                yield element
        if isinstance(arg, str):
            yield arg
        if isinstance(arg, bytes):
            yield arg.decode()
    if add_br:
        yield ' '*indent + "</li>\n"
    else:
        yield "</li>\n"

def html_bold(text, indent=0, add_br=True):
    if add_br:
        return ' '*indent + f"<b>{text}</b><br>\n"
    else:
        return ' '*indent + f"<b>{text}</b> "

def html_fixed_width_from_file(input_file, indent=0):
    yield "<pre>\n"

    with open(input_file, 'r') as out:
        for line in out.readlines():
            yield line

    yield "</pre>\n"

def html_fixed_width_from_str(input_str, indent=0):
    yield "<pre>\n"

    for line in input_str.split("\n"):
        yield line + "\n"

    yield "</pre>\n"

def html_header():
    return (
        "<head>" +
        "<script>\n" +
        importlib.resources.read_text(resources, "bootstrap.min.js") +
        "\n</script>\n" +
        "<script>\n" +
        importlib.resources.read_text(resources, "Chart.bundle.min.js") +
        "\n</script>\n" +
        "<style>\n" +
        importlib.resources.read_text(resources, "bootstrap.min.css") +
        "\n</style>\n" +
        "<style>\n" +
        importlib.resources.read_text(resources, "Chart.min.css") +
        "\n</style>\n" +
        "</head>"
    )

