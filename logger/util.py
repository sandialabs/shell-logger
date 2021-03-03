#!/usr/bin/env python3
from . import resources
from collections.abc import Iterable, Mapping
import datetime
import pkgutil
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

def miliseconds_to_datetime(miliseconds):
    return datetime.datetime.fromtimestamp(miliseconds / 1000.0)

def miliseconds_to_human_time(miliseconds):
    return miliseconds_to_datetime(miliseconds).strftime('%Y-%m-%d %H:%M:%S.%f')

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

def command_card(message, duration, *args):
    indent = ' '*8
    header, footer = split_template(command_template,
                                    "more_info",
                                    message=message,
                                    duration=duration)
    yield header
    for arg in args:
        if isinstance(arg, str):
            yield textwrap.indent(arg, indent)
        elif isinstance(arg, Iterable):
            for _arg in arg:
                yield textwrap.indent(_arg, indent)
    yield footer

def message_card(text):
    indent = ' '*8
    header, footer = split_template(message_template, "message")
    yield header
    yield textwrap.indent(text.replace('\n', "<br>\n"), indent) + '\n'
    yield footer

def command_detail_list(cmd_id, *args):
    indent = ' '*16
    header, footer = split_template(command_detail_list_template,
                                    "details",
                                    cmd_id=cmd_id)
    yield header
    for arg in args:
        if isinstance(arg, str):
            yield textwrap.indent(arg, indent)
    yield footer

def command_detail(cmd_id, name, value, hidden=False):
    if hidden:
        return hidden_command_detail_template.format(cmd_id=cmd_id,
                                                     name=name,
                                                     value=value)
    else:
        return command_detail_template.format(name=name, value=value)

def stat_chart_card(labels, data, title, id):
    yield stat_chart_template.format(labels=labels,
                                     data=data,
                                     title=title,
                                     id=id)

def output_block_card(title, string, cmd_id):
    name = title.replace(' ', '_').lower()
    indent = ' '*12
    header, footer = split_template(output_block_card_template,
                                    "output_block",
                                    name=name,
                                    title=title,
                                    cmd_id=cmd_id)
    yield header
    for line in output_block(string, name, cmd_id):
        yield textwrap.indent(line, indent)
    yield footer

def output_block(input, name, cmd_id):
    if isinstance(input, Path):
        with open(input) as f:
            for string in output_block_html(f, name, cmd_id):
                yield string
    if isinstance(input, str):
        for string in output_block_html(input, name, cmd_id):
            yield string

def diagnostics_card(cmd_id, *args):
    indent = ' '*16

    header, footer = split_template(diagnostics_template,
                                    "diagnostics",
                                    cmd_id=cmd_id)
    yield header
    for arg in args:
        if isinstance(arg, str):
            yield textwrap.indent(arg, indent)
        elif isinstance(arg, Iterable):
            for _arg in arg:
                yield textwrap.indent(_arg, indent)
    yield footer

def output_block_html(lines, name, cmd_id):
    indent = ' '*12
    if isinstance(lines, str):
        lines = lines.split('\n')
    header, footer = split_template(output_block_template,
                                    "table_contents",
                                    name=name,
                                    cmd_id=cmd_id)
    yield header
    lineno = 0
    for line in lines:
        lineno += 1
        yield textwrap.indent(output_line_html(line, lineno), indent)
    yield footer

def split_template(template, split_at, **kwargs):
    split_marker = bytes([4]).decode()
    placeholder = template.format(**{**kwargs, split_at: split_marker})
    before, after = placeholder.split(split_marker + '\n')
    return before, after

def output_line_html(line, lineno):
    encoded_line = html_encode(line).rstrip()
    return output_line_template.format(line=encoded_line, lineno=lineno)

def html_encode(text):
    text = text.replace('&', "&amp;")
    text = text.replace('<', "&lt;")
    text = text.replace('>', "&gt;")
    text = text.replace('-', "-&#8288;") # non breaking dashes
    return text

def html_header():
    return (
        "<head>" +
        embed_style("bootstrap.min.css") +
        embed_style("Chart.min.css") +
        embed_style("command_style.css") +
        embed_style("detail_list_style.css") +
        embed_style("code_block_style.css") +
        embed_style("output_style.css") +
        embed_style("diagnostics_style.css") +
        embed_style("stat_chart_style.css") +
        embed_script("jquery.slim.min.js") +
        embed_script("bootstrap.bundle.min.js") +
        embed_script("Chart.bundle.min.js") +
        embed_script("search_output.js") +
        "</head>"
    )

def embed_style(resource):
    return (
        "<style>\n" +
        pkgutil.get_data(__name__, f"resources/{resource}").decode() +
        "\n</style>\n"
    )

def embed_script(resource):
    return (
        "<script>\n" +
        pkgutil.get_data(__name__, f"resources/{resource}").decode() +
        "\n</script>\n"
    )

def load_template(template):
    template_file = f"resources/templates/{template}"
    return pkgutil.get_data(__name__, template_file).decode()

command_detail_list_template   = load_template("command_detail_list.html")
command_detail_template        = load_template("command_detail.html")
hidden_command_detail_template = load_template("hidden_command_detail.html")
stat_chart_template            = load_template("stat_chart.html")
diagnostics_template           = load_template("diagnostics.html")
output_block_card_template     = load_template("output_block_card.html")
output_block_template          = load_template("output_block.html")
output_line_template           = load_template("output_line.html")
message_template               = load_template("message.html")
command_template               = load_template("command.html")

