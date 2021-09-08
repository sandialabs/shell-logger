#!/usr/bin/env python3
from collections.abc import Iterable, Mapping
from datetime import datetime
import pkgutil
from pathlib import Path
import re
from src.shelllogger import ShellLogger
import textwrap
from types import SimpleNamespace
from typing import Iterator, List, TextIO, Tuple, Union


def nested_simplenamespace_to_dict(namespace: object) -> object:
    """
    Todo:  Figure this out.

    Parameters:
        namespace:  Todo

    Returns:
        Todo
    """
    if "_asdict" in dir(namespace):
        return nested_simplenamespace_to_dict(namespace._asdict())
    elif isinstance(namespace, (str, bytes, tuple)):
        return namespace
    elif isinstance(namespace, Mapping):
        return {k: nested_simplenamespace_to_dict(v) for k, v in
                namespace.items()}
    elif isinstance(namespace, Iterable):
        return [nested_simplenamespace_to_dict(x) for x in namespace]
    elif isinstance(namespace, SimpleNamespace):
        return nested_simplenamespace_to_dict(namespace.__dict__)
    else:
        return namespace


def get_human_time(milliseconds: float) -> str:
    """
    Get a human-readable date/time.

    Parameters:
        milliseconds:  The number of milliseconds since epoch.

    Returns:
        A string representation of the date and time.
    """
    return datetime.fromtimestamp(milliseconds / 1000.0).strftime(
        '%Y-%m-%d %H:%M:%S.%f'
    )


def opening_html_text() -> str:
    """
    Get the opening HTML text.

    Returns:
        A string containing the first line of the HTML document through
        ``</head>``.
    """
    return ("<!DOCTYPE html>"
            + "<html>"
            + html_header())


def closing_html_text() -> str:
    """
    Get the closing HTML tag.

    Returns:
        A string with the closing HTML tag in it.
    """
    return "</html>"


def append_html(*args: object, output: Path) -> None:
    """
    Todo:  Figure this out.

    Parameters:
        *args:  Todo
        output:  The HTML file to append to.
    """

    def _append_html(f: TextIO, *inner_args: object) -> None:
        """
        Todo:  Figure this out.

        Parameters:
            f:  The HTML file to write to.
            *inner_args:  Todo
        """
        for arg in inner_args:
            if isinstance(arg, str):
                f.write(arg)
            elif isinstance(arg, bytes):
                f.write(arg.decode())
            elif isinstance(arg, Iterable):
                _append_html(f, *arg)
            else:
                raise RuntimeError(f"Unsupported type: {type(arg)}")

    with open(output, "a") as output_file:
        _append_html(output_file, *args)


def fixed_width(text: str) -> str:
    """
    Wrap the given ``text`` in a ``<code>...</code>`` block such that it
    displays in a fixed-width font.

    Parameters:
        text:  The text to wrap.

    Returns:
        The ``<code>...</code>`` block.
    """
    return f"<code>{html_encode(text)}</code>"


def flatten(element: Union[str, bytes, Iterable]) -> Iterator[str]:
    """
    Takes a tree of lists and turns it into a flat iterable of strings.

    Parameters:
        element:  An element of a tree.

    Yields:
        The string representation of the given element.
    """
    if isinstance(element, str):
        yield element
    elif isinstance(element, bytes):
        yield element.decode()
    elif isinstance(element, Iterable):
        for _element in element:
            yield from flatten(_element)
    else:
        yield element


def parent_logger_card_html(name: str, *args: Iterator[str]) -> Iterator[str]:
    """
    Generate the HTML for the card corresponding to the parent
    :class:`ShellLogger`.  The HTML elements are yielded one at a time
    to avoid loading *all* the data from the :class:`ShellLogger` into
    memory at once.

    Parameters:
        name:  The name of the :class:`ShellLogger`.
        *args:  A list of generators to lazily yield string HTML
            elements for the contents of the parent card.

    Yields:
        The header, followed by all the contents of the
        :class:`ShellLogger`, and then the footer.
    """
    header, indent, footer = split_template(parent_logger_template,
                                            "parent_body",
                                            name=name)
    yield header
    for arg in flatten(args):
        yield textwrap.indent(arg, indent)
    yield footer


def child_logger_card(log: ShellLogger) -> Iterator[str]:
    """
    Create a card to go in the HTML log file containing everything
    pertaining to a child :class:`ShellLogger`.

    Parameters:
        log:  The child :class:`ShellLogger` for which to generate the
            card.

    Returns:
        A generator that will lazily yield the elements of the HTML for
        the card one at a time.
    """
    child_html = log.to_html()
    return child_logger_card_html(log.name, log.duration, *child_html)


def child_logger_card_html(
        name: str,
        duration: str,
        *args: Union[Iterator[str], List[Iterator[str]]]
) -> Iterator[str]:
    """
    Generate the HTML for a card corresponding to the child
    :class:`ShellLogger`.  The HTML elements are yielded one at a time
    to avoid loading *all* the data from the :class:`ShellLogger` into
    memory at once.

    Parameters:
        name:  The name of the child :class:`ShellLogger`.
        duration:  The duration of the child :class:`ShellLogger`.
        *args:  A generator (or list of generators) to lazily yield
            string HTML elements for the contents of the child card.

    Yields:
        The header, followed by all the contents of the child
        :class:`ShellLogger`, and then the footer.

    Todo:
      * Should we replace the ``for`` loop with the one found in
        :func:`parent_logger_card_html`?
    """
    header, indent, footer = split_template(child_logger_template,
                                            "child_body",
                                            name=name,
                                            duration=duration)
    yield header
    for arg in args:
        if isinstance(arg, str):
            yield textwrap.indent(arg, indent)
        elif isinstance(arg, Iterable):
            for _arg in arg:
                yield textwrap.indent(_arg, indent)
    yield footer


def command_card_html(log: dict, *args: object) -> Iterator[str]:
    """
    Generate the HTML for a card corresponding to a command that was
    run.  The HTML elements are yielded one at a time to avoid loading
    *all* the data into memory at once.

    Parameters:
        log:  An entry from the :class:`ShellLogger` 's log book
            corresponding to a command that was run.
        *args:  Todo

    Yields:
        The header, followed by all the contents of the command card,
        and then the footer.
    """
    header, indent, footer = split_template(command_template,
                                            "more_info",
                                            cmd_id=log["cmd_id"],
                                            command=fixed_width(log["cmd"]),
                                            message=log["msg"],
                                            return_code=log["return_code"],
                                            duration=log["duration"])
    yield header
    for arg in args:
        if isinstance(arg, str):
            yield textwrap.indent(arg, indent)
        elif isinstance(arg, Iterable):
            for _arg in arg:
                yield textwrap.indent(_arg, indent)
    yield footer


def html_message_card(log: dict) -> Iterator[str]:
    """
    Generate the HTML for a card corresponding to a message to only be
    included in the HTML log file (e.g., not printed to ``stdout`` as
    well).

    Parameters:
        log:  An entry from the :class:`ShellLogger` 's log book
            corresponding to a message.

    Yields:
        The header, followed by the contents of the message card, and
        then the footer.
    """
    timestamp = (
        log["timestamp"]
        .replace(' ', '_')
        .replace(':', '-')
        .replace('/', '_')
        .replace('.', '-')
    )
    header, indent, footer = split_template(html_message_template,
                                            "message",
                                            title=log["msg_title"],
                                            timestamp=timestamp)
    text = html_encode(log["msg"])
    text = "<pre>" + text.replace('\n', "<br>") + "</pre>"
    yield header
    yield textwrap.indent(text, indent) + '\n'
    yield footer


def message_card(log: dict) -> Iterator[str]:
    """
    Generate the HTML for a card corresponding to a message to be both
    printed to ``stdout`` and included in the HTML log file.

    Parameters:
        log:  An entry from the :class:`ShellLogger` 's log book
            corresponding to a message.

    Yields:
        The header, followed by the contents of the message card, and
        then the footer.
    """
    header, indent, footer = split_template(message_template, "message")
    text = html_encode(log["msg"])
    text = "<pre>" + text.replace('\n', "<br>") + "</pre>"
    yield header
    yield textwrap.indent(text, indent) + '\n'
    yield footer


def command_detail_list(cmd_id: str, *args: Iterable[str]) -> Iterator[str]:
    """
    Generate the HTML for a list of details associated with a command
    that was run.

    Parameters:
        cmd_id:  The unique identifier associated with the command that
            was run.
        *args:  All of the details associated with a command that was
            run.

    Yields:
        The header, followed by each of the details associated with the
        command that was run, and then the footer.
    """
    header, indent, footer = split_template(command_detail_list_template,
                                            "details",
                                            cmd_id=cmd_id)
    yield header
    for arg in args:
        if isinstance(arg, str):
            yield textwrap.indent(arg, indent)
    yield footer


def command_detail(
        cmd_id: str,
        name: str,
        value: str,
        hidden: bool = False
) -> str:
    """
    Create the HTML snippet for a detail associated with a command that
    was run.

    Parameters:
        cmd_id:  The unique identifier associated with the command that
            was run.
        name:  The name of the detail being recorded.
        value:  The value of the detail being recorded.
        hidden:  Whether or not this detail should be hidden (collapsed)
            in the HTML by default.

    Returns:
        The HTML snippet for this command detail.
    """
    if hidden:
        return hidden_command_detail_template.format(cmd_id=cmd_id,
                                                     name=name,
                                                     value=value)
    else:
        return command_detail_template.format(name=name, value=value)


def command_card(log: dict, stream_dir: Path) -> Iterator[str]:
    """
    Todo:  Figure this out.

    Parameters:
        log:  An entry from the :class:`ShellLogger` 's log book
            corresponding to a command that was run.
        stream_dir:  The stream directory containing the ``stdout``,
            ``stderr``, and ``trace`` output from the command.

    Returns:
        A generator to lazily yield the elements of the command card one
        at a time.
    """
    cmd_id = log["cmd_id"]
    stdout_path = stream_dir / f"{log['timestamp']}_{cmd_id}_stdout"
    stderr_path = stream_dir / f"{log['timestamp']}_{cmd_id}_stderr"
    trace_path = stream_dir / f"{log['timestamp']}_{cmd_id}_trace"

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
            disk_stats = {x: y for x, y in log["stats"]["disk"].items()
                          if x not in uninteresting_disks}
            # We sort because JSON deserialization may change
            # the ordering of the map.
            for disk, data in sorted(disk_stats.items()):
                diagnostics.append(disk_timeseries_plot(cmd_id, data, disk))
    info.append(diagnostics_card(cmd_id, *diagnostics))

    return command_card_html(log, *info)


def timeseries_plot(cmd_id: object, data_tuples: object, series_title: object) -> object:
    """
    Todo:  Figure this out.

    Parameters:
        cmd_id:  The unique identifier associated with the command that
            was run.
        data_tuples:
        series_title:

    Returns:

    """
    labels = [get_human_time(x) for x, _ in data_tuples]
    values = [y for _, y in data_tuples]
    id = f"{cmd_id}-{series_title.lower().replace(' ', '-')}-chart"
    return stat_chart_card(labels, values, series_title, id)


def disk_timeseries_plot(cmd_id: object, data_tuples: object, volume_name: object) -> object:
    """
    Todo:  Figure this out.

    Parameters:
        cmd_id:  The unique identifier associated with the command that
            was run.
        data_tuples:
        volume_name:

    Returns:

    """
    labels = [get_human_time(x) for x, _ in data_tuples]
    values = [y for _, y in data_tuples]
    id = f"{cmd_id}-volume{volume_name.replace('/', '_')}-usage"
    stat_title = f"Used Space on {volume_name}"
    return stat_chart_card(labels, values, stat_title, id)


def stat_chart_card(labels: object, data: object, title: object, id: object) -> object:
    """
    Todo:  Figure this out.

    Parameters:
        labels:
        data:
        title:
        id:
    """
    yield stat_chart_template.format(labels=labels,
                                     data=data,
                                     title=title,
                                     id=id)


def output_block_card(
        title: str,
        output: Union[Path, str],
        cmd_id: str,
        collapsed: bool = True
) -> Iterator[str]:
    """
    Given the output from a command, generate a corresponding HTML card
    for inclusion in the log file.

    Parameters:
        title:  The title for the output block.
        output:  The output from a command.
        cmd_id:  The unique identifier associated with the command that
            was run.
        collapsed:  Whether or not the output block should be collapsed
            by default in the HTML log file.

    Yields:
        The header, followed by each line of the output, and then the
        footer.
    """
    name = title.replace(' ', '_').lower()
    template = (output_card_collapsed_template if collapsed else
                output_card_template)
    header, indent, footer = split_template(template,
                                            "output_block",
                                            name=name,
                                            title=title,
                                            cmd_id=cmd_id)
    yield header
    for line in output_block(output, name, cmd_id):
        yield textwrap.indent(line, indent)
    yield footer


def output_block(
        output: Union[Path, str],
        name: str,
        cmd_id: str
) -> Iterator[str]:
    """
    Given the output from a command, generate the HTML equivalent for
    inclusion in the log file.

    Parameters:
        output:  The output from a command.
        name:  The name (title) of the output block.
        cmd_id:  The unique identifier associated with the command that
            was run.

    Yields:
        The HTML equivalent of each line of the output in turn.
    """
    if isinstance(output, Path):
        with open(output) as f:
            for string in output_block_html(f, name, cmd_id):
                yield string
    if isinstance(output, str):
        for string in output_block_html(output, name, cmd_id):
            yield string


def diagnostics_card(cmd_id: object, *args: object) -> Iterator[str]:
    """
    Todo:  Figure this out.

    Parameters:
        cmd_id:  The unique identifier associated with the command that
            was run.
        *args:
    """
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


def output_block_html(
        lines: Union[TextIO, str],
        name: str,
        cmd_id: str
) -> Iterator[str]:
    """
    Given the output of a command, generate its HTML equivalent for
    inclusion in the log file.

    Parameters:
        lines:  The lines of output.
        name:  The name (title) for this output block.
        cmd_id:  The unique identifier associated with the command that
            was run.

    Yields:
        The header, followed by the HTML corresponding to each line of
        output, and then the footer.
    """
    if isinstance(lines, str):
        lines = lines.split('\n')
    header, indent, footer = split_template(output_block_template,
                                            "table_contents",
                                            name=name,
                                            cmd_id=cmd_id)
    yield header
    line_no = 0
    for line in lines:
        line_no += 1
        yield textwrap.indent(output_line_html(line, line_no), indent)
    yield footer


def split_template(
        template: str,
        split_at: str,
        **kwargs
) -> Tuple[str, str, str]:
    """
    Take a templated HTML snippet and split it into a header and footer,
    meaning everything that comes before and after the line containing
    ``split_at``.  Also determine the indentation for the content that
    will be inserted between the header and footer.

    Example:
        If the following snippet is ``template`` and ``split_at`` is
        ``child_body``, then the header is lines 1-6, the footer is
        lines 8-9, and the indent is eight spaces.

        .. code-block:: html
           :linenos:
           :emphasize-lines: 7

           <details class="child-logger">
               <summary>
                   <h6 class="child-logger-heading">{name}</h6>
                   <span class="duration"> (Duration: {duration})</span>
               </summary>
               <div class="child-logger-body">
                   {child_body}
               </div>
           </details>

    Parameters:
        template:  A templated HTML snippet.
        split_at:  A substring used to split the ``template`` into
            before and after chunks.
        **kwargs:  Additional keyword arguments used to replace keywords
            in the ``template``.

    Returns:
        The header, indent, and footer.
    """
    fmt = {k: v for k, v in kwargs.items() if k != split_at}
    pattern = re.compile(f"(.*\\n)(\\s*)\\{{{split_at}\\}}\\n(.*)",
                         flags=re.DOTALL)
    before, indent, after = pattern.search(template).groups()
    return before.format(**fmt), indent, after.format(**fmt)


def output_line_html(line: str, line_no: int) -> str:
    """
    Given a line of output from a command, along with the corresponding
    line number, create the HTML equivalent to be included in the log
    file.

    Parameters:
        line:  A line of output.
        line_no:  The corresponding line number.

    Returns:
        The corresponding HTML snippet.
    """
    encoded_line = html_encode(line).rstrip()
    return output_line_template.format(line=encoded_line, line_no=line_no)


def html_encode(text: str) -> str:
    """
    Replace special characters with their HTML encodings.

    Parameters:
        text:  The text to encode.

    Returns:
        The encoded text.
    """
    text = text.replace('&', "&amp;")
    text = text.replace('<', "&lt;")
    text = text.replace('>', "&gt;")
    text = text.replace('-', "-&#8288;")  # Non-breaking dashes.
    text = sgr_to_html(text)
    return text


def sgr_to_html(text: object) -> object:
    """
    Todo:  Figure this out.

    Parameters:
        text:

    Returns:

    """
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


def sgr_4bit_color_and_style_to_html(sgr: object) -> object:
    """
    Todo:  Figure this out.

    Parameters:
        sgr:

    Returns:

    """
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


def sgr_8bit_color_to_html(sgr_params: object) -> object:
    """
    Todo:  Figure this out.

    Parameters:
        sgr_params:

    Returns:

    """
    sgr_256 = int(sgr_params[2]) if len(sgr_params) > 2 else 0
    if sgr_256 < 0 or sgr_256 > 255 or not sgr_params:
        '<span>'
    if 15 < sgr_256 < 232:
        red_6cube = (sgr_256 - 16) // 36
        green_6cube = (sgr_256 - (16 + red_6cube * 36)) // 6
        blue_6cube = (sgr_256 - 16) % 6
        red = str(51 * red_6cube)
        green = str(51 * green_6cube)
        blue = str(51 * blue_6cube)
        return sgr_24bit_color_to_html([sgr_params[0], "2", red, green, blue])
    elif 231 < sgr_256 < 256:
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


def sgr_24bit_color_to_html(sgr_params: object) -> object:
    """
    Todo:  Figure this out.

    Parameters:
        sgr_params:

    Returns:

    """
    r, g, b = sgr_params[2:5] if len(sgr_params) == 5 else ("0", "0", "0")
    if len(sgr_params) > 1 and sgr_params[:2] == ["38", "2"]:
        return f'<span style="color: rgb({r}, {g}, {b})">'
    elif len(sgr_params) > 1 and sgr_params[:2] == ["48", "2"]:
        return f'<span style="background-color: rgb({r}, {g}, {b})">'
    else:
        return '<span>'


def html_header() -> str:
    """
    Get the HTML header, complete with embedded styles and scripts.

    Returns:
        A string with the ``<head>...</head>`` contents.
    """
    return ("<head>"
            + embed_style("bootstrap.min.css")
            + embed_style("Chart.min.css")
            + embed_style("top_level_style_adjustments.css")
            + embed_style("parent_logger_style.css")
            + embed_style("child_logger_style.css")
            + embed_style("command_style.css")
            + embed_style("message_style.css")
            + embed_style("detail_list_style.css")
            + embed_style("code_block_style.css")
            + embed_style("output_style.css")
            + embed_style("diagnostics_style.css")
            + embed_style("search_controls.css")
            + embed_script("jquery.slim.min.js")
            + embed_script("bootstrap.bundle.min.js")
            + embed_script("Chart.bundle.min.js")
            + embed_script("search_output.js")
            + embed_html("search_icon.svg")
            + "</head>")


def embed_style(resource: str) -> str:
    """
    Wrap the given ``resource`` in an appropriate ``<style>...</style>``
    block for embedding in the HTML header.

    Parameters:
        resource:  The name of a style file to embed.

    Returns:
        A string containing the ``<style>...</style>`` block.

    Todo:
      * Combine this with the two below?
    """
    return ("<style>\n"
            + pkgutil.get_data(__name__, f"resources/{resource}").decode()
            + "\n</style>\n")


def embed_script(resource: str) -> str:
    """
    Wrap the given ``resource`` in an appropriate
    ``<script>...</script>`` block for embedding in the HTML header.

    Parameters:
        resource:  The name of a script file to embed.

    Returns:
        A string containing the ``<script>...</script>`` block.
    """
    return ("<script>\n"
            + pkgutil.get_data(__name__, f"resources/{resource}").decode()
            + "\n</script>\n")


def embed_html(resource: str) -> str:
    """
    Get a HTML ``resource`` froma file for the sake of embedding it into
    the HTML header.

    Parameters:
        resource:  The name of a HTML file to embed.

    Returns:
        The contents of the file.

    Todo:
      * Why do we use ``pkgutil.get_data()`` instead of a simple
        ``read()``.
    """
    return pkgutil.get_data(__name__, f"resources/{resource}").decode()


def load_template(template: str) -> str:
    """
    Load a template HTML file.

    Parameters:
        template:  The file name to load.

    Returns:
        A string containing the contents of the file.

    Todo:
      * Combine with the one above?
    """
    template_file = f"resources/templates/{template}"
    return pkgutil.get_data(__name__, template_file).decode()


command_detail_list_template = load_template("command_detail_list.html")
command_detail_template = load_template("command_detail.html")
hidden_command_detail_template = load_template("hidden_command_detail.html")
stat_chart_template = load_template("stat_chart.html")
diagnostics_template = load_template("diagnostics.html")
output_card_template = load_template("output_card.html")
output_card_collapsed_template = load_template("output_card_collapsed.html")
output_block_template = load_template("output_block.html")
output_line_template = load_template("output_line.html")
message_template = load_template("message.html")
html_message_template = load_template("html_message.html")
command_template = load_template("command.html")
child_logger_template = load_template("child_logger.html")
parent_logger_template = load_template("parent_logger.html")
