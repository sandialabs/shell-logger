#!/usr/bin/env python3
import datetime
from distutils.dir_util import copy_tree
import json
import os
import pathlib
import random
import re
import shutil
import string
import sys
import tempfile
import common_functions as cf


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
            logger_dict = obj.__dict__
            logger_dict.update({'__type__': 'Logger'})
            return logger_dict
        elif isinstance(obj, datetime.datetime):
            time = {
                '__type__': 'datetime',
                'value': obj.strftime('%Y-%m-%d_%H:%M:%S:%f'),
                'format': '%Y-%m-%d_%H:%M:%S:%f'
            }
            return time
        elif isinstance(obj, pathlib.Path):
            path = {
                '__type__': 'Path'
                'value': str(obj),
            }
            return path
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
            return pathlib.Path(obj['value'])


class Logger():
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
        log_dir (str):  Path to where the logs are stored for the parent
            :class:`Logger` and all its children.
        name (str):  The name of the :class:`Logger` object.
        strm_dir (str):  Path to directory where ``stdout``/``stderr`` stream
            logs are stored.
        html_file (str):  Path to main HTML file for the parent and
            children :class:`Logger` objects.
        indent (int):  The indentation level of this :class:`Logger` object.
            The parent has a level 0. Each successive child's indent is
            increased by 1.
    """

    def __init__(self, name, log_dir, strm_dir=None, html_file=None, indent=0,
                 log=None, init_time=None, done_time=None, duration=None):
        """
        Parameters:
            name (str):  Name to give to this Logger object.
            log_dir (str):  Path to directory where log files will be stored.
            strm_dir (str):  Path to directory where ``stdout``/``stderr``
                stream logs are stored.  This is helpful for parent Logger
                objects to give to child Logger objects in order to keep things
                in the same directory.
            html_file (str):  Path to main HTML file for the parent and
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
        self.init_time = datetime.datetime.now() if not init_time else\
            init_time
        self.done_time = datetime.datetime.now() if not done_time else\
            done_time
        self.duration = duration
        self.indent = indent
        self.is_parent = True if self.indent == 0 else False

        # log_dir
        # -------
        self.log_dir = pathlib.Path(log_dir).resolve()
        if not log_dir.exists():
            log_dir.mkdir(parents=True, exist_ok=True)

        # strm_dir
        # -------
        # If there isn't a strm_dir given by the parent Logger, this is the
        # parent. Create the strm_dir.
        if strm_dir is None:
            now = self.init_time.strftime("%Y-%m-%d_%H.%M.%S.%f_")
            self.strm_dir = (
                pathlib.Path(tempfile.mkdtemp(dir=self.log_dir, prefix=now))
            )
        else:
            self.strm_dir = pathlib.Path(strm_dir)

        # html_file
        # ---------
        if html_file is not None:
            self.html_file = pathlib.Path(html_file)

            # Usually, this is only the case if loading from a JSON file when
            # the HTML file has been removed.
            if not html_file.exists():
                logger_name = html_file.name
                logger_name = re.match("(.*).html$", logger_name).group(1)
                html_text = f"<h1>{logger_name} Log</h1>"

                # Write the file.
                with open(self.html_file, 'w') as f:
                    f.write(html_text)
        else:
            # If there isn't an HTML file, this is that parent Logger object,
            # and it needs to create the main HTML file.
            self.html_file = self.strm_dir / (name.replace(' ', '_') + '.html')
            html_text = f"<h1>{self.name} Log</h1>"

            # Write the file.
            with open(self.html_file, 'w') as f:
                f.write(html_text)

    def log(self, msg, cmd, cwd=os.getcwd(), live_stdout=False,
            live_stderr=False, return_info=False, verbose=False):
        """
        Add something to the log. To conserve memory, ``stdout`` and ``stderr``
        will be written to the files as it is being generated.

        Parameters:
            msg (str):  Message to be recorded with the command. This could be
                documentation of what your command is doing and its purpose.
            cmd (str, list):  Shell command to be executed.
            cwd (str):  Path to the working directory of the command to be
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

        Returns:
            dict:  A dictionary containing `stdout`, `stderr`, and
            `return_code` keys.  If `return_info` is set to ``False``,
            the `stdout` and `stderr` values will be ``None``.
        """

        start_time = datetime.datetime.now()

        # Create a unique command ID that will be used to find the location
        # of the stdout/stderr files in the temporary directory during
        # finalization.
        cmd_id = 'cmd_' + ''.join(random.choice(string.ascii_lowercase)
                                  for i in range(9))

        # Create a string form of the command to be stored.
        if isinstance(cmd, list):
            cmd_str = ' '.join(cmd)
        else:
            cmd_str = cmd

        log = {
            'msg': msg,
            'duration': None,
            'timestamp': start_time.strftime("%Y-%m-%d_%H%M%S"),
            'cmd': cmd_str,
            'cmd_id': cmd_id,
            'cwd': str(cwd),
            'return_code': 0,
        }

        # Create & open files for stdout and stderr
        time_str = start_time.strftime("%Y-%m-%d_%H%M%S")
        stdout_path = self.strm_dir / f"{time_str}_{cmd_id}_stdout"
        stderr_path = self.strm_dir / f"{time_str}_{cmd_id}_stderr"

        with open(stdout_path, 'a') as out, open(stderr_path, 'a') as err:
            # Print the command to be executed.
            if verbose:
                print(cmd_str)

            if return_info:
                stdout = ''
                stderr = ''

            # Write to stdout/stderr files as text is being returned.
            generator = cf.run_cmd_generator(cmd, cwd)
            for result in generator:
                if result['stdout'] is not None:
                    if live_stdout:
                        print(result['stdout'], end='')
                        # Just to be sure it's printing out right.
                        sys.stdout.flush()
                    if return_info:
                        # Generally, '\r' characters aren't wanted here
                        clean_stdout = re.sub('\r', '', result['stdout'])
                        stdout += clean_stdout
                    out.write(result['stdout'])

                elif result['stderr'] is not None:
                    if live_stderr:
                        print(result['stderr'], end='', file=sys.stderr)
                        # Just to be sure it's printing out right.
                        sys.stderr.flush()
                    if return_info:
                        # Generally, '\r' characters aren't wanted here
                        clean_stderr = re.sub('\r', '', result['stderr'])
                        stderr += clean_stderr
                    err.write(result['stderr'])

                # Execution is finished when stdout & stderr are both None
                else:
                    log['return_code'] = result['return_code']

        # Update a few things.
        end_time = datetime.datetime.now()
        log['duration'] = self.strfdelta(end_time-start_time,
                                         "{hrs}h {min}m {sec}s")
        self.log_book.append(log)

        if return_info:
            return {'return_code': log['return_code'], 'stdout': stdout,
                    'stderr': stderr}
        else:
            return {'return_code': log['return_code'], 'stdout': None,
                    'stderr': None}

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
            new_log_dir (str):  Path to the new :attr:`log_dir`.
        """

        abs_new_log_dir = pathlib.Path(new_log_dir).resolve()

        # This only gets executed once by the top-level parent Logger object.
        if self.log_dir.exists():
            copy_tree(self.log_dir, abs_new_log_dir)
            shutil.rmtree(self.log_dir)

        # Change the strm_dir, html_file, and log_dir for every child Logger
        # recursively.
        self.strm_dir = abs_new_log_dir / os.path.relpath(self.strm_dir,
                                                          self.log_dir)
        self.html_file = abs_new_log_dir / os.path.relpath(self.html_file,
                                                           self.log_dir)
        self.log_dir = pathlib.Path(new_log_dir).abspath()
        for log in self.log_book:
            if isinstance(log, Logger):
                log.change_log_dir(new_log_dir)

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
            tdelta (datetime.timedelta): Time delta object.
            fmt (str): Delta format string. Use like :func:`datetime.strftime`.

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

        for log in self.log_book:
            i = self.indent * 2  # Each indent is 2 spaces

            # Child Logger
            # ------------
            if isinstance(log, Logger):
                # Update the duration of this Logger's commands
                if log.duration is None:
                    log.__update_duration()

                # First print the header text.
                html_str = (
                    ' '*i + "\n<br>\n" +
                    ' '*i + "<details>\n" +
                    ' '*i + "  <summary>\n" +
                    ' '*i + "    <b><font " +
                    f"size='6'>{log.name}</font></b>\n" +
                    ' '*i + f"    <br>Duration: {log.duration}\n" +
                    ' '*i + "  </summary>"
                )
                with open(self.html_file, 'a') as html:
                    html.write(html_str)

                # Let the child Logger save its own commands into HTML
                log.finalize()

                # Save the ending HTML
                html_str = ' '*i + "</details>"
                with open(self.html_file, 'a') as html:
                    html.write(html_str)

                # Skip the regular log entry stuff
                continue

            # Message Log Entry
            # -----------------
            if log['cmd'] is None:
                html_str = log['msg'].replace('\n', '\n' + ' '*i + '<br>')
                html_str = '\n' + ' '*i + '<br>' + html_str
                with open(self.html_file, 'a') as html:
                    html.write(html_str)

                # Skip the regular log entry stuff
                continue

            # Command Log Entry
            # -----------------
            # Write the top part of the HTML entry
            html_str = (
                '\n' +
                ' '*i + "<br>\n" +
                ' '*i + "<details>\n" +
                ' '*i + "  <summary>\n" +
                ' '*i + f"    <b>{log['msg']}</b>\n" +
                ' '*i + f"    <br>Duration: {log['duration']}\n" +
                ' '*i + "  </summary>\n" +
                ' '*i + "  <ul>\n" +
                ' '*i + f"    <li><b>Time:</b> {log['timestamp']}</li>\n" +
                ' '*i + f"    <li><b>Command:</b> {log['cmd']}</li>\n" +
                ' '*i + f"    <li><b>CWD:</b> {log['cwd']}</li>\n" +
                ' '*i + "    <li><b>Return Code:</b> " +
                f"{log['return_code']}</li>\n" +
                ' '*i + "    <li>\n" +
                ' '*i + "      <b>stdout:</b>\n"
            )
            with open(self.html_file, 'a') as html:
                html.write(html_str)

            # Append the stdout of this command to the HTML file
            cmd_id = log['cmd_id']
            stdout_path = self.strm_dir / f"{log['timestamp']}_{cmd_id}_stdout"
            with open(stdout_path, 'r') as out,\
                    open(self.html_file, 'a') as html:
                for line in out:
                    html_line = ' '*i + "      <br>" + line
                    html.write(html_line)

            # Append HTML text between end of stdout and beginning of stderr.
            html_str = (
                ' '*i + "    </li>\n" +
                ' '*i + "    <li>\n" +
                ' '*i + "      <b>stderr:</b><br>\n"
            )
            with open(self.html_file, 'a') as html:
                html.write(html_str)

            # Append the stderr of this command to the HTML file
            stderr_path = self.strm_dir / f"{log['timestamp']}_{cmd_id}_stderr"
            with open(stderr_path, 'r') as err,\
                    open(self.html_file, 'a') as html:
                for line in err:
                    html_line = ' '*i + "      <br>" + line
                    html.write(html_line)

            # Append concluding HTML for this command to the HTML file.
            html_str = (
                ' '*i + "    </li>\n" +
                ' '*i + "  </ul>\n" +
                ' '*i + "</details>"
            )
            with open(self.html_file, 'a') as html:
                html.write(html_str)

        # Final steps (Only for the parent)
        # ---------------------------------
        if self.is_parent:
            # Create a symlink in log_dir to the HTML file in strm_dir.
            curr_html_file = self.html_file.name
            new_location = self.log_dir / curr_html_file
            temp_link_name = pathlib.Path(tempfile.mktemp(dir=self.log_dir))
            temp_link_name.symlink_to(self.html_file)
            pathlib.Path(temp_link_name).replace(new_location)

            # Save everything to a JSON file in the timestamped strm_dir
            json_file = self.name.replace(' ', '_') + '.json'
            json_file = self.strm_dir / json_file

            with open(json_file, 'w') as jf:
                json.dump(self, jf, cls=LoggerEncoder, sort_keys=True, indent=4)
