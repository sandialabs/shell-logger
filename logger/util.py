#!/usr/bin/env python3
from collections.abc import Iterable, Mapping
import datetime
import pkgutil
import os
from pathlib import Path
import re
import textwrap
from types import SimpleNamespace, GeneratorType

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
    def _append_html(file, *args):
        for arg in args:
            if isinstance(arg, str):
                file.write(arg)
            elif isinstance(arg, bytes):
                file.write(arg.decode())
            elif isinstance(arg, Iterable):
                _append_html(file, *element)
            else:
                raise RuntimeError(f"Unsupported type: {type(arg)}")
    with open(output, "a") as file:
        _append_html(file, *args)

def fixed_width(text):
    return f"<code>{html_encode(text)}</code>"

def flatten(element):
    if isinstance(element, str):
        yield element
    elif isinstance(element, bytes):
        file.write(element.decode())
    elif isinstance(element, Iterable):
        for _element in element:
            yield from flatten(_element)
    else:
        yield element

def parent_logger_card_html(name, *args):
    header, indent, footer = split_template(parent_logger_template,
                                            "parent_body",
                                            name=name)
    yield header
    for arg in flatten(args):
        yield textwrap.indent(arg, indent)
    yield footer

def child_logger_card(log):
    heading = f"h{min(log.indent + 1, 4)}"
    child_html = log.to_html()
    return child_logger_card_html(log.name, heading, log.duration, *child_html)

def child_logger_card_html(name, heading, duration, *args):
    header, indent, footer = split_template(child_logger_template,
                                            "child_body",
                                            name=name,
                                            heading=heading,
                                            duration=duration)
    yield header
    for arg in args:
        if isinstance(arg, str):
            yield textwrap.indent(arg, indent)
        elif isinstance(arg, Iterable):
            for _arg in arg:
                yield textwrap.indent(_arg, indent)
    yield footer

def command_card_html(message, duration, *args):
    header, indent, footer = split_template(command_template,
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

def html_message_card(log):
    timestamp = log["timestamp"]
    timestamp = timestamp.replace(' ', '_')
    timestamp = timestamp.replace(':', '-')
    timestamp = timestamp.replace('/', '_')
    timestamp = timestamp.replace('.', '-')
    header, indent, footer = split_template(html_message_template,
                                            "message",
                                            title=log["msg_title"],
                                            timestamp=timestamp)
    text = html_encode(log["msg"])
    text = "<pre>" + text.replace('\n', "<br>") + "</pre>"
    yield header
    yield textwrap.indent(text, indent) + '\n'
    yield footer

def message_card(log):
    header, indent, footer = split_template(message_template, "message")
    text = html_encode(log["msg"])
    text = "<pre>" + text.replace('\n', "<br>") + "</pre>"
    yield header
    yield textwrap.indent(text, indent) + '\n'
    yield footer

def command_detail_list(cmd_id, *args):
    header, indent, footer = split_template(command_detail_list_template,
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

def command_card(log, strm_dir):
    cmd_id = log["cmd_id"]
    stdout_path = strm_dir / f"{log['timestamp']}_{cmd_id}_stdout"
    stderr_path = strm_dir / f"{log['timestamp']}_{cmd_id}_stderr"
    trace_path = strm_dir / f"{log['timestamp']}_{cmd_id}_trace"

    info = [
        command_detail_list(
            cmd_id,
            command_detail(cmd_id, "Time", log["timestamp"]),
            command_detail(cmd_id, "Command", fixed_width(log["cmd"])),
            command_detail(cmd_id, "CWD", log["pwd"], hidden=True),
            command_detail(cmd_id, "Hostname", log["hostname"], hidden=True),
            command_detail(cmd_id, "User", log["user"], hidden=True),
            command_detail(cmd_id, "Group", log["group"], hidden=True),
            command_detail(cmd_id, "Shell", log["shell"], hidden=True),
            command_detail(cmd_id, "umask", log["umask"], hidden=True),
            command_detail(cmd_id, "Return Code", log["return_code"])
        ),
        output_block_card("stdout", stdout_path, cmd_id, collapsed=False),
        output_block_card("stderr", stderr_path, cmd_id, collapsed=False),
    ]

    diagnostics = [
        output_block_card("Environment", log["environment"], cmd_id),
        output_block_card("ulimit", log["ulimit"], cmd_id),
    ]
    if trace_path.exists():
        diagnostics.append(output_block_card("trace", trace_path, cmd_id))

    if log.get("stats"):
        stats = [("memory", "Memory Usage"), ("cpu", "CPU Usage")]
        for stat, stat_title in stats:
            if log["stats"].get(stat):
                data = log["stats"][stat]
                diagnostics.append(timeseries_plot(cmd_id, data, stat_title))
        if log["stats"].get("disk"):
            uninteresting_disks = ["/var", "/var/log", "/var/log/audit",
                                   "/boot", "/boot/efi"]
            disk_stats = { x:y for x, y in log["stats"]["disk"].items()
                           if x not in uninteresting_disks }
            # We sort because JSON deserialization may change
            # the ordering of the map.
            for disk, data in sorted(disk_stats.items()):
                diagnostics.append(disk_timeseries_plot(cmd_id, data, disk))
    info.append(diagnostics_card(cmd_id, *diagnostics))

    return command_card_html(log["msg"], log["duration"], *info)

def timeseries_plot(cmd_id, data_tuples, series_title):
    labels = [miliseconds_to_human_time(x) for x, _ in data_tuples]
    values = [y for _, y in data_tuples]
    id = f"{cmd_id}-{series_title.lower().replace(' ', '-')}-chart"
    return stat_chart_card(labels, values, series_title, id)

def disk_timeseries_plot(cmd_id, data_tuples, volume_name):
    labels = [miliseconds_to_human_time(x) for x, _ in data_tuples]
    values = [y for _, y in data_tuples]
    id = f"{cmd_id}-volume{volume_name.replace('/', '_')}-usage"
    stat_title = f"Used Space on {volume_name}"
    return stat_chart_card(labels, values, stat_title, id)

def stat_chart_card(labels, data, title, id):
    yield stat_chart_template.format(labels=labels,
                                     data=data,
                                     title=title,
                                     id=id)

def output_block_card(title, string, cmd_id, collapsed=True):
    name = title.replace(' ', '_').lower()
    if collapsed:
        template = output_card_collapsed_template
    else:
        template = output_card_template
    header, indent, footer = split_template(template,
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
    header, indent, footer = split_template(diagnostics_template,
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
    if isinstance(lines, str):
        lines = lines.split('\n')
    header, indent, footer = split_template(output_block_template,
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
    format = { k:v for k, v in kwargs.items() if k != split_at }
    pattern = re.compile(f"(.*\\n)(\\s*)\\{{{split_at}\\}}\\n(.*)",
                         flags=re.DOTALL)
    before, indent, after = pattern.search(template).groups()
    return before.format(**format), indent, after.format(**format)

def output_line_html(line, lineno):
    encoded_line = html_encode(line).rstrip()
    return output_line_template.format(line=encoded_line, lineno=lineno)

def html_encode(text):
    text = text.replace('&', "&amp;")
    text = text.replace('<', "&lt;")
    text = text.replace('>', "&gt;")
    text = text.replace('-', "-&#8288;") # non breaking dashes
    text = sgr_to_html(text)
    return text

def sgr_to_html(text):
    span_count = 0
    while text.find("\x1b[") >= 0:
        start = text.find("\x1b[")
        finish = text.find("m", start)
        sgrs = text[start+2:finish].split(';')
        span_string = ""
        if len(sgrs) == 0:
            span_string += "</span>" * span_count
            span_count = 0
        else:
            while sgrs:
                if sgrs[0] == "0":
                    span_string += "</span>" * span_count
                    span_count = 0
                    sgrs = sgrs[1:]
                elif len(sgrs) >= 5 and sgrs[:2] in [["38", "2"], ["48", "2"]]:
                    span_count += 1
                    span_string += sgr_24bit_color_to_html(sgrs[:5])
                    sgrs = sgrs[5:]
                elif len(sgrs) >= 3 and sgrs[:2] in [["38", "5"], ["48", "5"]]:
                    span_count += 1
                    span_string += sgr_8bit_color_to_html(sgrs[:3])
                    sgrs = sgrs[3:]
                else:
                    span_count += 1
                    span_string += sgr_4bit_color_and_style_to_html(sgrs[0])
                    sgrs = sgrs[1:]
        text = text[:start] + span_string + text[finish+1:]
    return text

def sgr_4bit_color_and_style_to_html(sgr):
    sgr_to_css = {
        "1": "font-weight: bold;",
        "2": "font-weight: lighter;",
        "3": "font-style: italic;",
        "4": "text-decoration: underline;",
        "9": "text-decoration: line-through;",
        "30": "color: black;",   "40":  "background-color: black;",
        "31": "color: red;",     "41":  "background-color: red;",
        "32": "color: green;",   "42":  "background-color: green;",
        "33": "color: yellow;",  "43":  "background-color: yellow;",
        "34": "color: blue;",    "44":  "background-color: blue;",
        "35": "color: magenta;", "45":  "background-color: magenta;",
        "36": "color: cyan;",    "46":  "background-color: cyan;",
        "37": "color: white;",   "47":  "background-color: white;",
        "90": "color: black;",   "100": "background-color: black;",
        "91": "color: red;",     "101": "background-color: red;",
        "92": "color: green;",   "102": "background-color: green;",
        "93": "color: yellow;",  "103": "background-color: yellow;",
        "94": "color: blue;",    "104": "background-color: blue;",
        "95": "color: magenta;", "105": "background-color: magenta;",
        "96": "color: cyan;",    "106": "background-color: cyan;",
        "97": "color: white;",   "107": "background-color: white;",
        "39": "color: inherit;", "49":  "background-color: inherit;",
    }
    return f'<span style="{sgr_to_css.get(sgr) or str()}">'

def sgr_8bit_color_to_html(sgr_params):
    sgr_256 = int(sgr_params[2]) if len(sgr_params) > 2 else 0
    if sgr_256 < 0 or sgr_256 > 255 or not sgr_params:
        '<span>'
    if sgr_256 > 15 and sgr_256 < 232:
        red_6cube = (sgr_256 - 16) // 36
        green_6cube = (sgr_256 - (16 + red_6cube * 36)) // 6
        blue_6cube = (sgr_256 - 16) % 6
        red = str(51 * red_6cube)
        green = str(51 * green_6cube)
        blue = str(51 * blue_6cube)
        return sgr_24bit_color_to_html([sgr_params[0], "2", red, green, blue])
    elif sgr_256 < 256 and sgr_256 > 231:
        gray = str(8 + (sgr_256 - 232) * 10)
        return sgr_24bit_color_to_html([sgr_params[0], "2", gray, gray, gray])
    elif sgr_params[0] == "38":
        if sgr_256 < 8:
            return sgr_4bit_color_and_style_to_html(str(30+sgr_256))
        elif sgr_256 < 16:
            return sgr_4bit_color_and_style_to_html(str(82+sgr_256))
    elif sgr_params[0] == "48":
        if sgr_256 < 8:
            return sgr_4bit_color_and_style_to_html(str(40+sgr_256))
        elif sgr_256 < 16:
            return sgr_4bit_color_and_style_to_html(str(92+sgr_256))

def sgr_24bit_color_to_html(sgr_params):
    r, g, b = sgr_params[2:5] if len(sgr_params) == 5 else ("0", "0", "0")
    if len(sgr_params) > 1 and sgr_params[:2] == ["38","2"]:
        return f'<span style="color: rgb({r}, {g}, {b})">'
    elif len(sgr_params) > 1 and sgr_params[:2] == ["48","2"]:
        return f'<span style="background-color: rgb({r}, {g}, {b})">'
    else:
        return '<span>'

def html_header():
    return (
        "<head>" +
        embed_style("bootstrap.min.css") +
        embed_style("Chart.min.css") +
        embed_style("parent_logger_style.css") +
        embed_style("child_logger_style.css") +
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
output_card_template           = load_template("output_card.html")
output_card_collapsed_template = load_template("output_card_collapsed.html")
output_block_template          = load_template("output_block.html")
output_line_template           = load_template("output_line.html")
message_template               = load_template("message.html")
html_message_template          = load_template("html_message.html")
command_template               = load_template("command.html")
child_logger_template          = load_template("child_logger.html")
parent_logger_template         = load_template("parent_logger.html")

