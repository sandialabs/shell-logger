#!/usr/bin/env python3

from .classes import Shell, Trace, StatsCollector, Stat, trace_collector, stats_collectors
from .util import make_svg_line_chart, nested_SimpleNamespace_to_dict, filter_junk_from_env, opening_html_text, closing_html_text, append_html, html_fixed_width_from_file, html_fixed_width_from_str, html_bold, html_list_item, html_details, simple_detail_list_item, simple_detail_collapsed_list_item, output_block_from_file, output_block_from_str, stat_chart, simple_details_list, inline_fixed_width
from collections.abc import Iterable, Mapping
import datetime
import distutils.dir_util as dir_util
import json
import os
from pathlib import Path
import psutil
import random
import re
import select
import shutil
import string
import tempfile
import time
from types import SimpleNamespace


class LoggerEncoder(json.JSONEncoder):
    """
    This is a helper class to make the :class:`Logger` class JSON serializable.
    This particular class is used in the process of saving :class:`Logger`
    objects to JSON.

    Usage::

        import json
        with open('path_to_json_file', 'w') as jf:
            json.dump(data, jf, cls=LoggerEncoder)

    """
    def default(self, obj):
        if isinstance(obj, Logger):
            logger = {
                **{'__type__': 'Logger'},
                **{k:self.default(v) for k, v in obj.__dict__.items()}
            }
            return logger
        elif isinstance(obj, (int, float, str, bytes)):
            return obj
        elif isinstance(obj, Mapping):
            return {k:self.default(v) for k,v in obj.items()}
        elif isinstance(obj, tuple):
            tup = {
                '__type__': 'tuple',
                'items': obj
            }
            return tup
        elif isinstance(obj, Iterable):
            return [ self.default(x) for x in obj ]
        elif isinstance(obj, datetime.datetime):
            time = {
                '__type__': 'datetime',
                'value': obj.strftime('%Y-%m-%d_%H:%M:%S:%f'),
                'format': '%Y-%m-%d_%H:%M:%S:%f'
            }
            return time
        elif isinstance(obj, Path):
            path = {
                '__type__': 'Path',
                'value': str(obj)
            }
            return path
        elif obj is None:
            return None
        elif isinstance(obj, Shell):
            shell = {
                '__type__': 'Shell',
                'pwd': obj.pwd()
            }
            return shell
        else:
            # Call JSONEncoder's implementation
            return json.JSONEncoder.default(self, obj)


class LoggerDecoder(json.JSONDecoder):
    """
    This is a helper class to make the :class:`Logger` class JSON serializable.
    This particular class is used in the process of retrieving :class:`Logger`
    objects from JSON.

    Usage::

        import json
        with open('path_to_json_file', 'r') as jf:
            logger = json.load(jf, cls=LoggerDecoder)

    """
    def __init__(self):
        json.JSONDecoder.__init__(self, object_hook=self.dict_to_object)

    def dict_to_object(self, obj):
        """
        This converts data dictionaries given by the JSONDecoder into objects
        of type :class:`Logger`, :class:`datetime.datetime`, etc.
        """
        if '__type__' not in obj:
            return obj
        elif obj['__type__'] == 'Logger':
            logger = Logger(obj['name'], obj['log_dir'],
                            obj['strm_dir'], obj['html_file'], obj['indent'],
                            obj['log_book'], obj['init_time'],
                            obj['done_time'], obj['duration'])
            return logger
        elif obj['__type__'] == 'datetime':
            return datetime.datetime.strptime(obj['value'], obj['format'])
        elif obj['__type__'] == 'Path':
            return Path(obj['value'])
        elif obj['__type__'] == 'tuple':
            return tuple(obj['items'])
        elif obj['__type__'] == 'Shell':
            return Shell(Path(obj['pwd']))


class Logger:
    """
    This class will keep track of commands run in the shell, their durations,
    descriptions, ``stdout``, ``stderr``, and ``return_code``.  When the
    :func:`finalize` method is called, the :class:`Logger` object will
    aggregate all the data from its commands and child :class:`Logger` objects
    (see example below) into both JSON and HTML files.

    Example::

        > Parent Logger Object Name
            Duration: 18h 20m 35s
          > cmd1  (Click arrow '>' to expand for more details)
            Duration: 0.25s
          > Child Logger Object Name (i.e. Trilinos)
            Duration: 3h 10m 0s
            > Child Logger Object Name (i.e. Configure)
              Duration: 1m 3s
              > cmd1
        etc...

    Note:
        Because some ``stdout``/``stderr`` streams can be quite long, they will
        be written to files in a temporary directory
        (``log_dir/tmp/YYYY-MM-DD_hh:mm:ss/``).  Once the :func:`finalize`
        method is called, they will be aggregated in an HTML file
        (``log_dir/html_file``).  The JSON file (``log_dir/json_file``) will
        contain references to the ``stdout``/``stderr`` files so that an HTML
        file can be recreated again later if needed.

    Attributes:
        done_time (datetime):  The time this :class:`Logger` object is done
            with its commands/messages.
        duration (str):  String formatted duration of this :class:`Logger`,
            updated when the :func:`finalize` method is called.
        init_time (datetime):  The time this :class:`Logger` object was
            created.
        log (list):  A list containing log entries and child.
            :class:`Logger` objects in the order they were created.
        log_dir (Path):  Path to where the logs are stored for the parent
            :class:`Logger` and all its children.
        name (str):  The name of the :class:`Logger` object.
        strm_dir (Path):  Path to directory where ``stdout``/``stderr`` stream
            logs are stored.
        html_file (Path):  Path to main HTML file for the parent and
            children :class:`Logger` objects.
        indent (int):  The indentation level of this :class:`Logger` object.
            The parent has a level 0. Each successive child's indent is
            increased by 1.
    """

    def __init__(self, name, log_dir=Path.cwd(), strm_dir=None, html_file=None,
                 indent=0, log=None, init_time=None, done_time=None,
                 duration=None):
        """
        Parameters:
            name (str):  Name to give to this Logger object.
            log_dir (Path):  Path to directory where log files will be stored.
            strm_dir (Path):  Path to directory where ``stdout``/``stderr``
                stream logs are stored.  This is helpful for parent Logger
                objects to give to child Logger objects in order to keep things
                in the same directory.
            html_file (Path):  Path to main HTML file for the parent and
                children Logger objects. If ``None`` (default), this is the
                parent Logger object, and it will need to create the file.
            indent (int):  The indentation level of this Logger object. The
                parent has a level 0. Each successive child's indent is
                increased by 1.
            log (list):  Optionally provide an existing log list to the
                :class:`Logger` object.  This is mainly used when importing
                :class:`Logger` objects from a JSON file, and can generally be
                left at the default value - an empty list.
            init_time (datetime):  Optionally provide an init_time to the
                :class:`Logger` object.  This is mainly used when importing
                :class:`Logger` objects from a JSON file, and can generally be
                left at the default value - the current time.
            done_time (datetime):  Optionally provide a done_time to the
                :class:`Logger` object.  This is mainly used when importing
                :class:`Logger` objects from a JSON file, and can generally be
                left at the default value - the current time.
        """

        # Misc
        # ----
        self.name = name
        self.log_book = log if log is not None else []
        self.init_time = datetime.datetime.now() if not init_time else init_time
        self.done_time = datetime.datetime.now() if not done_time else done_time
        self.duration = duration
        self.indent = indent
        self.is_parent = True if self.indent == 0 else False
        self.shell = Shell(Path.cwd())

        # log_dir
        # -------
        self.log_dir = log_dir.resolve()
        if not log_dir.exists():
            log_dir.mkdir(parents=True, exist_ok=True)

        # strm_dir
        # -------
        # If there isn't a strm_dir given by the parent Logger, this is the
        # parent. Create the strm_dir.
        if strm_dir is None:
            now = self.init_time.strftime("%Y-%m-%d_%H.%M.%S.%f_")
            self.strm_dir = Path(tempfile.mkdtemp(dir=self.log_dir,
                                                  prefix=now))
        else:
            self.strm_dir = strm_dir.resolve()

        # html_file
        # ---------
        if html_file is not None:
            self.html_file = html_file.resolve()
        else:
            self.html_file = self.strm_dir / (name.replace(' ', '_') + '.html')

        if self.is_parent:
            html_text = opening_html_text() + "\n"
            with open(self.html_file, 'w') as f:
                f.write(html_text)


    def update_done_time(self):
        """
        Allows the ``done_time`` to be updated before
        :func:`finalize` is called.  This is especially useful for child
        :class:`Logger` objects who might finish their commands before the
        parent finalizes everything.
        """
        self.done_time = datetime.datetime.now()

    def __update_duration(self):
        """
        Updates the `duration` attribute with the time from the beginning of
        the :class:`Logger` object's creation until now.
        """
        self.update_done_time()
        dur = self.done_time - self.init_time
        self.duration = self.strfdelta(dur, "{hrs}h {min}m {sec}s")

    def check_duration(self):
        """
        Returns the current duration from the beginning of the :class:`Logger`
        object's creation until now.

        Returns:
            str:  Duration from this object's creation until now as a string.
        """
        now = datetime.datetime.now()
        dur = now - self.init_time
        return self.strfdelta(dur, "{hrs}h {min}m {sec}s")

    def change_log_dir(self, new_log_dir):
        """
        Change the :attr:`log_dir` of this :class:`Logger` object and all
        children recursively.

        Warning:
            Only run this method on the top-level parent :class:`Logger`
            object!  Otherwise, parents and children in a tree will have
            different :attr:`log_dir` 's and things will break.

        Parameters:
            new_log_dir (Path):  Path to the new :attr:`log_dir`.
        """

        # This only gets executed once by the top-level parent Logger object.
        if self.log_dir.exists():
            dir_util.copy_tree(self.log_dir, new_log_dir)
            shutil.rmtree(self.log_dir)

        # Change the strm_dir, html_file, and log_dir for every child Logger
        # recursively.
        self.strm_dir = new_log_dir / self.strm_dir.relative_to(self.log_dir)
        self.html_file = new_log_dir / self.html_file.relative_to(self.log_dir)
        self.log_dir = new_log_dir.resolve()
        for log in self.log_book:
            if isinstance(log, Logger):
                log.change_log_dir(self.log_dir)

    def add_child(self, child_name):
        """
        Creates and returns a 'child' :class:`Logger` object. This will be one
        step indented in the tree of the output log (see example in class
        docstring). The total time for this child will be recorded when the
        :func:`finalize` method is called in the child object.

        Parameters:
            child_name (str):  Name of the child :class:`Logger` object.

        Returns:
            Logger:  Child :class:`Logger` object.
        """

        # Create the child object and add it to the list of children.
        child = Logger(child_name, self.log_dir, self.strm_dir, self.html_file,
                       self.indent+1)
        self.log_book.append(child)

        return child

    def strfdelta(self, tdelta, fmt):
        """
        Format a time delta object.

        Parameters:
            tdelta (datetime.datetime.timedelta): Time delta object.
            fmt (str): Delta format string. Use like
                       :func:`datetime.datetime.strftime`.

        Returns:
            str: String with the formatted time delta.
        """

        # Dictionary to hold time delta info.
        d = {'days': tdelta.days}
        total_ms = tdelta.microseconds + (tdelta.seconds * 1000000)
        d['hrs'], rem = divmod(total_ms, 3600000000)
        d['min'], rem = divmod(rem, 60000000)
        d['sec'] = rem / 1000000

        # Round to 2 decimals
        d['sec'] = round(d['sec'], 2)

        # String template to help with recognizing the format.
        return fmt.format(**d)

    def print(self, msg, end='\n'):
        """
        Print a message and save it to the log.

        Parameters:
            msg (str):  Message to print and save to the log.
        """

        print(msg, end=end)
        log = {
            'msg': msg,
            'timestamp': str(datetime.datetime.now()),
            'cmd': None
        }
        self.log_book.append(log)

    def finalize(self):
        """
        This method iterates through each entry in this :class:`Logger`
        object's log list and appends corresponding HTML text to the main HTML
        file. For each entry, the ``stdout``/``stderr`` are copied from their
        respective files in the ``strm_dir``.
        """

        i = self.indent * 2  # Each indent is 2 spaces
        heading = f"h{min(self.indent + 1, 5)}"
        html_str = ' '*i + f"\n<{heading}>{self.name} Log</{heading}>\n"
        with open(self.html_file, 'a') as html:
            html.write(html_str)

        if self.is_parent:
            with open(self.html_file, 'a') as html:
                html.write('<div style="padding: 0 1% 1cm;">')

        for log in self.log_book:
            # Child Logger
            # ------------
            if isinstance(log, Logger):
                # Update the duration of this Logger's commands
                if log.duration is None:
                    log.__update_duration()

                heading = f"h{min(log.indent + 1, 5)}"
                # First print the header text.
                html_str = (
                    ' '*i + "<details>\n" +
                    ' '*i + "  <summary>\n" +
                    ' '*i + f"    <{heading} " +
                            'style="line-height: 1.5; display: inline;"' +
                            f">{log.name}</{heading}>\n" +
                    ' '*i + f"    <br>Duration: {log.duration}\n" +
                    ' '*i + "  </summary>" +
                    ' '*i + '  <div style="padding: 0 1.25%;">'
                )
                with open(self.html_file, 'a') as html:
                    html.write(html_str)

                # Let the child Logger save its own commands into HTML
                log.finalize()

                # Save the ending HTML
                html_str = ' '*i + "</div></details>"
                with open(self.html_file, 'a') as html:
                    html.write(html_str)

                # Skip the regular log entry stuff
                continue

            # Message Log Entry
            # -----------------
            if log['cmd'] is None:
                html_str = (
                    ' '*i + '<div class="card">\n' +
                    ' '*(i+2) + '<div class="card-body">\n' +
                    ' '*(i+4) + log['msg'].replace('\n', "<br>") + '\n' +
                    ' '*(i+2) + '</div>\n' +
                    ' '*i + '</div>\n'
                )
                with open(self.html_file, 'a') as html:
                    html.write(html_str)

                # Skip the regular log entry stuff
                continue

            # Command Log Entry
            # -----------------
            # Write the top part of the HTML entry
            html_str = (
                '\n' +
                ' '*i + "<details>\n" +
                ' '*i + "  <summary>\n" +
                ' '*i + "    <h6 " +
                        'style="line-height: 1.5; display: inline;"' +
                        f">{log['msg']}</h6>\n" +
                ' '*i + f"    <br>Duration: {log['duration']}\n" +
                ' '*i + "  </summary>\n" +
                ' '*i + '  <div style="padding: 0 2.5%;">'
            )
            with open(self.html_file, 'a') as html:
                html.write(html_str)

            cmd_id = log['cmd_id']
            stdout_path = self.strm_dir / f"{log['timestamp']}_{cmd_id}_stdout"
            stderr_path = self.strm_dir / f"{log['timestamp']}_{cmd_id}_stderr"
            trace_path = self.strm_dir / f"{log['timestamp']}_{cmd_id}_trace"
            filtered_env = filter_junk_from_env(log["environment"],
                                                [
                                                    "LS_COLORS",
                                                    "MANPATH",
                                                    "XDG_SESSION_ID",
                                                    "XDG_DATA_DIRS",
                                                    "HISTSIZE",
                                                    "KDEDIRS",
                                                    "LESSOPEN",
                                                ])

            append_html(
                simple_details_list(
                    simple_detail_list_item("Time", log["timestamp"], indent=4),
                    simple_detail_list_item("Command",
                                            inline_fixed_width(log["cmd"]),
                                            indent=4),
                    simple_detail_collapsed_list_item("CWD",
                                                      log["pwd"],
                                                      indent=4,
                                                      cmd_id=cmd_id),
                    simple_detail_collapsed_list_item("Hostname",
                                                      log["hostname"],
                                                      indent=4,
                                                      cmd_id=cmd_id),
                    simple_detail_collapsed_list_item("User",
                                                      log["user"],
                                                      indent=4,
                                                      cmd_id=cmd_id),
                    simple_detail_collapsed_list_item("Group",
                                                      log["group"],
                                                      indent=4,
                                                      cmd_id=cmd_id),
                    simple_detail_collapsed_list_item("Shell",
                                                      log["shell"],
                                                      indent=4,
                                                      cmd_id=cmd_id),
                    simple_detail_collapsed_list_item("umask",
                                                      log["umask"],
                                                      indent=4,
                                                      cmd_id=cmd_id),
                    simple_detail_list_item("Return Code",
                                            log["return_code"],
                                            indent=4),
                    cmd_id=cmd_id
                ),
                output_block_from_file("stdout",
                                       stdout_path,
                                       log["cmd_id"],
                                       expanded=True),
                output_block_from_file("stderr",
                                       stderr_path,
                                       log["cmd_id"],
                                       expanded=True),
                output=self.html_file
            )

            html_str = (
                '<div class="card" style="margin: 6pt 0 6pt">' +
                '<div class="card-body">' +
                '<h5 class="card-title" ' +
                'role="button" ' +
                f'data-target="#{cmd_id}-diagnostics" ' +
                'data-toggle="collapse"' +
                '>' +
                'Diagnostics' +
                '</h5>' +
                f'<div class="collapse" id="{cmd_id}-diagnostics">'
            )
            append_html(html_str, output=self.html_file)
            append_html(
                output_block_from_str("Environment",
                                      filtered_env,
                                      log["cmd_id"]),
                output_block_from_str("ulimit", log["ulimit"], log["cmd_id"]),
                output=self.html_file
            )
            if trace_path.exists():
                append_html(
                    output_block_from_file("trace", trace_path, log["cmd_id"]),
                    output=self.html_file
                )

            # Append HTML text between end of trace and beginning of
            # Memory Usage.
            if log["stats"]:
                if log["stats"]["memory"]:
                    x_offset = min([x for x, _ in log["stats"]["memory"]["data"]] + [0])
                    append_html(
                        '<div class="card" style="width: 47.5%; margin: 6pt 1.25% 0; float: left;">'
                        '<h5 class="card-title">Memory Usage</h5>'
                        '<div class="wrapper">',
                        f'<canvas id="{cmd_id}-mem-usage-chart">',
                        '</canvas>',
                        '</div>',
                        '</div>',
                        '<script>\n',
                        f'var chart = new Chart("{cmd_id}-mem-usage-chart", {{' + '\n',
                        '    type: "line",' + '\n',
                        '    data: {' + '\n',
                        '        labels: ',
                        str([datetime.datetime.fromtimestamp(x / 1000.0).strftime('%Y-%m-%d %H:%M:%S.%f') for x, _ in log["stats"]["memory"]["data"]]) + ",\n",
                        '        datasets: [{' + '\n',
                        '            label: "Memory Usage",' + '\n',
                        '            showLine: true,' + '\n',
                        '            lineTension: 0,' + '\n',
                        '            pointRadius: 0,' + '\n',
                        '            data: ',
                        str([y for _, y in log["stats"]["memory"]["data"]]) + '\n',
                        '        }]' + '\n',
                        '    },' + '\n',
                        '    options: {' + '\n',
                        '        legend: false,' + '\n',
                        '        scales: ',
                        '{yAxes:[{ticks:{beginAtZero:true,max:100,stepSize:100}}],xAxes:[{display:false}]}' + '\n',
                        '    }' + '\n',
                        '});' + '\n',
                        '</script>' + '\n',
                        output=self.html_file
                    )
                if log["stats"]["cpu"]:
                    x_offset = min([x for x, _ in log["stats"]["cpu"]["data"]] + [0])
                    append_html(
                        '<div class="card" style="width: 47.5%; margin: 6pt 1.25% 0; float: left;">'
                        '<h5 class="card-title">CPU Usage</h5>'
                        '<div class="wrapper">',
                        f'<canvas id="{cmd_id}-cpu-usage-chart">',
                        '</canvas>',
                        '</div>',
                        '</div>',
                        '<script>\n',
                        f'var chart = new Chart("{cmd_id}-cpu-usage-chart", {{' + '\n',
                        '    type: "line",' + '\n',
                        '    data: {' + '\n',
                        '        labels: ',
                        str([datetime.datetime.fromtimestamp(x / 1000.0).strftime('%Y-%m-%d %H:%M:%S.%f') for x, _ in log["stats"]["cpu"]["data"]]) + ",\n",
                        '        datasets: [{' + '\n',
                        '            label: "CPU Usage",' + '\n',
                        '            showLine: true,' + '\n',
                        '            lineTension: 0,' + '\n',
                        '            pointRadius: 0,' + '\n',
                        '            data: ',
                        str([y for _, y in log["stats"]["cpu"]["data"]]) + '\n',
                        '        }]' + '\n',
                        '    },' + '\n',
                        '    options: {' + '\n',
                        '        legend: false,' + '\n',
                        '        scales: ',
                        '{yAxes:[{ticks:{beginAtZero:true,max:100,stepSize:100}}],xAxes:[{display:false}]}' + '\n',
                        '    }' + '\n',
                        '});' + '\n',
                        '</script>' + '\n',
                        output=self.html_file
                    )
                if log["stats"]["disk"]:
                    # Append the disk usage of this command to
                    # the HTML file
                    # Note: we sort because JSON deserialization may change
                    # the ordering of the map.
                    for disk, stats in sorted(log["stats"]["disk"].items()):
                        if disk[:4] != "/var" and disk[:5] != "/boot":
                            x_offset = min([x for x, _ in stats["data"]] + [0])
                            html_id = cmd_id + '-' + "volume" + disk.replace("/", "_") + "-usage"
                            append_html(
                                '<div class="card" style="width: 47.5%; margin: 6pt 1.25% 0; float: left;">'
                                f'<h5 class="card-title">Used Space on {disk}</h5>'
                                '<div class="wrapper">',
                                f'<canvas id="{html_id}">',
                                '</canvas>',
                                '</div>',
                                '</div>',
                                '<script>\n',
                                f'var chart = new Chart("{html_id}", {{' + '\n',
                                '    type: "line",' + '\n',
                                '    data: {' + '\n',
                                '        labels: ',
                                str([datetime.datetime.fromtimestamp(x / 1000.0).strftime('%Y-%m-%d %H:%M:%S.%f') for x, _ in stats["data"]]) + ",\n",
                                '        datasets: [{' + '\n',
                                f'            label: "{disk} Usage",' + '\n',
                                '            showLine: true,' + '\n',
                                '            lineTension: 0,' + '\n',
                                '            pointRadius: 0,' + '\n',
                                '            data: ',
                                str([y for _, y in stats["data"]]) + '\n',
                                '        }]' + '\n',
                                '    },' + '\n',
                                '    options: {' + '\n',
                                '        legend: false,' + '\n',
                                '        scales: ',
                                '{yAxes:[{ticks:{beginAtZero:true,max:100,stepSize:100}}],xAxes:[{display:false}]}' + '\n',
                                '    }' + '\n',
                                '});' + '\n',
                                '</script>' + '\n',
                                output=self.html_file
                            )
                append_html('<div style="clear: left; margin-bottom: 6pt" />',
                            output=self.html_file)

            html_str = ' '*i + "</div></div></div></div></details>"
            with open(self.html_file, 'a') as html:
                html.write('\n')
                html.write(html_str)
                html.write('\n')

        # Final steps (Only for the parent)
        # ---------------------------------
        if self.is_parent:
            with open(self.html_file, 'a') as html:
                html.write("</div>")
                html.write(closing_html_text())
                html.write('\n')
            # Create a symlink in log_dir to the HTML file in strm_dir.
            curr_html_file = self.html_file.name
            new_location = self.log_dir / curr_html_file
            temp_link_name = Path(tempfile.mktemp(dir=self.log_dir))
            temp_link_name.symlink_to(self.html_file)
            temp_link_name.replace(new_location)

            # Save everything to a JSON file in the timestamped strm_dir
            json_file = self.name.replace(' ', '_') + '.json'
            json_file = self.strm_dir / json_file

            with open(json_file, 'w') as jf:
                json.dump(self, jf, cls=LoggerEncoder, sort_keys=True, indent=4)

    def log(self, msg, cmd, cwd=None, live_stdout=False,
            live_stderr=False, return_info=False, verbose=False,
            stdin_redirect=True, **kwargs):
        """
        Add something to the log. To conserve memory, ``stdout`` and ``stderr``
        will be written to the files as it is being generated.

        Parameters:
            msg (str):  Message to be recorded with the command. This could be
                documentation of what your command is doing and its purpose.
            cmd (str, list):  Shell command to be executed.
            cwd (Path):  Path to the working directory of the command to be
                executed.
            live_stdout (bool):  Print ``stdout`` as it is being produced as
                well as saving it to the file.
            live_stderr (bool):  Print ``stderr`` as it is being produced as
                well as saving it to the file.
            return_info (bool):  If set to ``True``, ``stdout``, ``stderr``,
                and ``return_code`` will be stored and returned in a
                dictionary.  Consider leaving this set to ``False`` if you
                anticipate your command producing large ``stdout``/``stderr``
                streams that could cause memory issues.
            verbose (bool):  Print the command before it is executed.
            stdin_redirect (bool):  Whether or not to redirect ``stdin`` to
                ``/dev/null``.  We do this by default to handle issues that
                arise when the ``cmd`` involves mpi; however, in some cases
                (e.g., involving ``bsub``) the redirect causes problems, and we
                need the flexibility to revert back to standard behavior.

        Returns:
            dict:  A dictionary containing `stdout`, `stderr`, `trace`, and
            `return_code` keys.  If `return_info` is set to ``False``,
            the `stdout` and `stderr` values will be ``None``. If `return_info`
            is set to ``True`` and `trace` is specified in kwargs, `trace` in
            the dictionary will contain the output of the specified trace;
            otherwise, it will be ``None``.
        """

        start_time = datetime.datetime.now()

        # Create a unique command ID that will be used to find the location
        # of the stdout/stderr files in the temporary directory during
        # finalization.
        cmd_id = 'cmd_' + ''.join(random.choice(string.ascii_lowercase)
                                  for i in range(9))

        if isinstance(cmd, list):
            cmd_str = ' '.join(str(x) for x in cmd)
        else:
            cmd_str = str(cmd)

        log = {
            'msg': msg,
            'duration': None,
            'timestamp': start_time.strftime("%Y-%m-%d_%H%M%S"),
            'cmd': cmd_str,
            'cmd_id': cmd_id,
            'cwd': cwd,
            'return_code': 0,
        }

        # Create & open files for stdout and stderr
        time_str = start_time.strftime("%Y-%m-%d_%H%M%S")
        stdout_path = self.strm_dir / f"{time_str}_{cmd_id}_stdout"
        stderr_path = self.strm_dir / f"{time_str}_{cmd_id}_stderr"
        trace_path = self.strm_dir / f"{time_str}_{cmd_id}_trace" if kwargs.get("trace") else None

        with open(stdout_path, 'a') as out, open(stderr_path, 'a') as err:
            # Print the command to be executed.
            if verbose:
                print(cmd_str)

        result = self.run(cmd_str,
                          quiet_stdout=not live_stdout,
                          quiet_stderr=not live_stderr,
                          stdout_str=return_info,
                          stderr_str=return_info,
                          trace_str=return_info,
                          stdout_path=stdout_path,
                          stderr_path=stderr_path,
                          trace_path=trace_path,
                          devnull_stdin=stdin_redirect,
                          pwd=cwd,
                          **kwargs)

        hrs = int(result.wall / 3600000)
        min = int(result.wall / 60000) % 60
        sec = int(result.wall / 1000) % 60
        log["duration"] = f"{hrs}h {min}m {sec}s"
        log["return_code"] = result.returncode
        log = {**log, **nested_SimpleNamespace_to_dict(result)}

        self.log_book.append(log)

        return {'return_code': log['return_code'],
                'stdout': result.stdout, 'stderr': result.stderr}

    def run(self, command, **kwargs):
        completed_process, trace_output = None, None
        collectors = stats_collectors(**kwargs)
        stats = {} if len(collectors) > 0 else None
        for key in ["stdout_str", "stderr_str", "trace_str"]:
            if key not in kwargs:
                kwargs[key] = True
        old_pwd = os.getcwd()
        if kwargs.get("pwd"):
            self.shell.cd(kwargs.get("pwd"))
        aux_info = self.auxiliary_information()
        for collector in collectors:
            collector.start()
        if "trace" in kwargs:
            trace = trace_collector(**kwargs)
            command = trace.command(command, **kwargs)
            trace_output = trace.output_path
        completed_process = self.shell.run(command, **kwargs)
        for collector in collectors:
            stats[collector.stat_name] = collector.finish()
        setattr(completed_process, "trace_path", trace_output)
        setattr(completed_process, "stats", stats)
        if kwargs.get("trace_str") and trace_output:
            with open(trace_output) as f:
                setattr(completed_process, "trace", f.read())
        else:
            setattr(completed_process, "trace", None)
        if kwargs.get("pwd"):
            self.shell.cd(old_pwd)
        return SimpleNamespace(**completed_process.__dict__, **aux_info.__dict__)

    def auxiliary_information(self):
        pwd, _ = self.shell.auxiliary_command(posix="pwd", nt="cd", strip=True)
        environment, _ = self.shell.auxiliary_command(posix="env", nt="set")
        umask, _ = self.shell.auxiliary_command(posix="umask", strip=True)
        hostname, _ = self.shell.auxiliary_command(posix="hostname", nt="hostname", strip=True)
        user, _ = self.shell.auxiliary_command(posix="whoami", nt="whoami", strip=True)
        group, _ = self.shell.auxiliary_command(posix="id -gn", strip=True)
        shell, _ = self.shell.auxiliary_command(posix="printenv SHELL", strip=True)
        ulimit, _ = self.shell.auxiliary_command(posix="ulimit -a")
        x = SimpleNamespace(
            pwd=pwd,
            environment=environment,
            umask=umask,
            hostname=hostname,
            user=user,
            group=group,
            shell=shell,
            ulimit=ulimit
        )
        return x

@Trace.subclass
class Strace(Trace):
    trace_name = "strace"
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.summary = True if kwargs.get("summary") else False
        self.expression = kwargs.get("expression")
    @property
    def trace_args(self):
        args = f"strace -f -o {self.output_path}"
        if self.summary:
            args += " -c"
        if self.expression:
            args += f" -e '{self.expression}'"
        return args

@Trace.subclass
class Ltrace(Trace):
    trace_name = "ltrace"
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.summary = True if kwargs.get("summary") else False
        self.expression = kwargs.get("expression")
    @property
    def trace_args(self):
        args = f"ltrace -C -f -o {self.output_path}"
        if self.summary:
            args += " -c"
        if self.expression:
            args += f" -e '{self.expression}'"
        return args

@StatsCollector.subclass
class DiskStatsCollector(StatsCollector):
    stat_name = "disk"
    def __init__(self, interval, manager):
        super().__init__(interval, manager)
        self.stats = manager.dict()
        self.mountpoints = [ p.mountpoint for p in psutil.disk_partitions() ]
        for m in self.mountpoints:
            self.stats[m] = manager.list()
    def collect(self):
        timestamp = round(time.time() * 1000)
        for m in self.mountpoints:
            self.stats[m].append((timestamp, psutil.disk_usage(m).percent))
    def unproxied_stats(self):
        def make_stat(stat):
            data = list(stat)
            svg = make_svg_line_chart(data)
            return Stat(data, svg)
        return {k:make_stat(v) for k,v in self.stats.items()}

@StatsCollector.subclass
class CPUStatsCollector(StatsCollector):
    stat_name = "cpu"
    def __init__(self, interval, manager):
        super().__init__(interval, manager)
        self.stats = manager.list()
    def collect(self):
        timestamp = round(time.time() * 1000)
        self.stats.append((timestamp, psutil.cpu_percent(interval=None)))
    def unproxied_stats(self):
        data = list(self.stats)
        svg = make_svg_line_chart(data)
        return Stat(data, svg)

@StatsCollector.subclass
class MemoryStatsCollector(StatsCollector):
    stat_name = "memory"
    def __init__(self, interval, manager):
        super().__init__(interval, manager)
        self.stats = manager.list()
    def collect(self):
        timestamp = round(time.time() * 1000)
        self.stats.append((timestamp, psutil.virtual_memory().percent))
    def unproxied_stats(self):
        data = list(self.stats)
        svg = make_svg_line_chart(data)
        return Stat(data, svg)

