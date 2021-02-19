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
import textwrap
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

def filter_junk_from_env(env, junk_list):
    filtered_env = ""
    for line in env.split('\n'):
        is_junk = any([line[:len(junk)+1] == f"{junk}=" for junk in junk_list])
        if not is_junk:
            filtered_env += line + '\n'
    return filtered_env

def opening_html_text():
    return (
        "<!DOCTYPE html>" +
        "<html>" +
        html_header()
    )

def closing_html_text():
    return "</html>"

def append_html(*args, output=None):
    with open(output, "a") as file:
        for arg in args:
            if isinstance(arg, GeneratorType):
                for element in arg:
                    file.write(element)
            if isinstance(arg, str):
                file.write(arg)
            if isinstance(arg, bytes):
                file.write(arg.decode())

def inline_fixed_width(text):
    return f"<code>{html_encode(text)}</code>"

def simple_details_list(*args, title="Details", indent=0, cmd_id=None):
    yield (
        ' '*indent + 
        '<div class="card" style="display: inline-block; margin-top: 6pt;">' +
        '<div class="card-body">' +
        '<ul class="list-group">\n'
    )
    if cmd_id:
        yield (
            '<h5 class="card-title" ' +
            'role="button" ' +
            f'data-target=".{cmd_id}-collapsible" ' +
            'data-toggle="collapse"' +
            '>' +
            f'{title}' +
            '</h5>'
        )
    else:
        yield f'<h5 class="card-title">{title}</h5>'
    for arg in args:
        if isinstance(arg, GeneratorType):
            for element in arg:
                yield element
        if isinstance(arg, str):
            yield arg
        if isinstance(arg, bytes):
            yield arg.decode()
    yield ' '*indent + f"</ul></div></div>\n"

def simple_detail_collapsed_list_item(name, value, cmd_id, indent=0):
    return html_list_item(
        html_bold(f"{name}:", add_br=False),
        str(value),
        indent=indent,
        add_br=False,
        element_class=f"list-group-item collapse {cmd_id}-collapsible"
    )

def simple_detail_list_item(name, value, indent=0):
    return html_list_item(
        html_bold(f"{name}:", add_br=False),
        str(value),
        indent=indent,
        add_br=False,
        element_class="list-group-item"
    )

def output_block_from_file(title, file, cmd_id, indent=0, expanded=False):
    yield (
        ' '*indent + 
        '<div class="card" style="margin-top: 6pt;">' +
        '<div class="card-body">' +
        '<ul class="list-group">\n'
    )
    element_id = cmd_id + '-' + title.replace(' ', '_')
    yield (
        '<h5 class="card-title" ' +
        'role="button" ' +
        f'data-target="#{element_id}" ' +
        'data-toggle="collapse"' +
        '>' +
        f'{title}' +
        '</h5>'
    )
    if expanded:
        yield f'<div class="collapse show" id={element_id}>'
    else:
        yield f'<div class="collapse" id={element_id}>'
    for element in html_fixed_width_from_file(file):
        yield element
    yield f'</div>'
    yield ' '*indent + f"</ul></div></div>\n"

def stat_chart(name, chart, indent=0):
    return html_list_item(
        html_bold(f"{name}:", indent=indent),
        textwrap.indent(chart, ' '*(indent+2)),
        indent=indent
    )

def output_block_from_str(title, string, cmd_id, indent=0, expanded=False):
    yield (
        ' '*indent + 
        '<div class="card" style="margin-top: 6pt;">' +
        '<div class="card-body">' +
        '<ul class="list-group">\n'
    )
    element_id = cmd_id + '-' + title.replace(' ', '_')
    yield (
        '<h5 class="card-title" ' +
        'role="button" ' +
        f'data-target="#{element_id}" ' +
        'data-toggle="collapse"' +
        '>' +
        f'{title}' +
        '</h5>'
    )
    if expanded:
        yield f'<div class="collapse show" id={element_id}>'
    else:
        yield f'<div class="collapse" id={element_id}>'
    for element in html_fixed_width_from_str(string):
        yield element
    yield f'</div>'
    yield ' '*indent + f"</ul></div></div>\n"

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

def html_list_item(*args, indent=0, add_br=True, element_class=None):
    li = "<li>" if element_class is None else f'<li class="{element_class}">'
    if add_br:
        yield ' '*indent + f"{li}\n"
    else:
        yield ' '*indent + f"{li}"
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
    yield "<pre><code>\n"

    with open(input_file, 'r') as out:
        for line in out.readlines():
            yield html_encode(line)

    yield "</code></pre>\n"

def html_fixed_width_from_str(input_str, indent=0):
    yield "<pre><code>\n"

    for line in input_str.split("\n"):
        yield html_encode(line) + '\n'

    yield "</code></pre>\n"

def html_encode(text):
    text = text.replace('&', "&amp;")
    text = text.replace('<', "&lt;")
    text = text.replace('>', "&gt;")
    text = text.replace('-', "-&#8288;") # non breaking dashes
    return text

def html_header():
    return (
        "<head>" +
        "<style>\n" +
        importlib.resources.read_text(resources, "bootstrap.min.css") +
        "\n</style>\n" +
        "<style>\n" +
        importlib.resources.read_text(resources, "Chart.min.css") +
        "\n</style>\n" +
        "<style>\n" +
        "code { color: inherit; }\n" +
        "pre { white-space: pre-wrap; }\n" +
        "\n</style>\n" +
        "<script>\n" +
        importlib.resources.read_text(resources, "jquery.slim.min.js") +
        "\n</script>\n" +
        "<script>\n" +
        importlib.resources.read_text(resources, "bootstrap.bundle.min.js") +
        "\n</script>\n" +
        "<script>\n" +
        importlib.resources.read_text(resources, "Chart.bundle.min.js") +
        "\n</script>\n" +
        "</head>"
    )

