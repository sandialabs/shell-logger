#!/usr/bin/env python3
import datetime
from distutils.dir_util import copy_tree
import json
import os
import random
import re
import shutil
import string
import sys
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
            logger = Logger(obj['top_dict']['name'], obj['log_dir'],
                            obj['tmp_dir'], obj['html_file'], obj['indent'],
                            obj['top_dict'])
            return logger
        elif obj['__type__'] == 'datetime':
            return datetime.datetime.strptime(obj['value'], obj['format'])


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
        top_dict (dict):  A dictionary containing the following:

            - **name** (`str`):  The name of the :class:`Logger` object.
            - **log** (`list`):  A list containing log entries and child
              :class:`Logger` objects in the order they were created.
            - **init_time** (`datetime`):  The time this :class:`Logger` object
              was created.
            - **done_time** (`datetime`):  The time this :class:`Logger` object
              is done with its commands/messages.

        log_dir (str):  Path to where the logs are stored for the parent
            :class:`Logger` and all its children.
        tmp_dir (str):  Path to temporary directory where in-progress log
            files are stored.
        html_file (str):  Path to main HTML file for the parent and
            children :class:`Logger` objects.
        indent (int):  The indentation level of this :class:`Logger` object.
            The parent has a level 0. Each successive child's indent is
            increased by 1.
    """

    def __init__(self, name, log_dir, tmp_dir=None, html_file=None, indent=0,
                 top_dict=None):
        """
        Parameters:
            name (str):  Name to give to this Logger object.
            log_dir (str):  Path to directory where log files will be stored.
            tmp_dir (str):  Path to temporary directory where in-progress log
                files are stored. This is helpful for parent Logger objects to
                give to child Logger objects in order to keep things in the
                same directory.
            html_file (str):  Path to main HTML file for the parent and
                children Logger objects. If ``None`` (default), this is the
                parent Logger object, and it will need to create the file.
            indent (int):  The indentation level of this Logger object. The
                parent has a level 0. Each successive child's indent is
                increased by 1.
            top_dict (dict):  Optionally provide the top_dict for this Logger
                object.  This is mainly used when importing Logger objects from
                a JSON file.  For general usage, leave this as ``None``.
        """

        # Misc
        # ----
        if top_dict is not None:
            self.top_dict = top_dict
        else:
            self.top_dict = {'name': name, 'log': [],
                             'init_time': datetime.datetime.now(),
                             'done_time': datetime.datetime.now()}
        self.log_dir = os.path.abspath(log_dir)
        self.indent = indent

        # log_dir
        # -------
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # tmp_dir
        # -------
        # If there isn't a tmp_dir given by the parent Logger, this is the
        # parent. Create the tmp_dir.
        if tmp_dir is None:
            top_tmp_dir = os.path.join(log_dir, 'tmp')
            if not os.path.exists(top_tmp_dir):
                os.makedirs(top_tmp_dir)
            now = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
            self.tmp_dir = os.path.join(top_tmp_dir, now)
            if not os.path.exists(self.tmp_dir):
                os.makedirs(self.tmp_dir)
        else:
            self.tmp_dir = tmp_dir

        # html_file
        # ---------
        if html_file is not None:
            self.html_file = html_file

            # Usually, this is only the case if loading from a JSON file when
            # the HTML file has been removed.
            if not os.path.exists(html_file):
                logger_name = html_file.split('/')[-1]
                logger_name = re.match("(.*).html$", logger_name).group(1)
                html_text = f"<h1>{logger_name} Log</h1>"

                # Write the file.
                with open(self.html_file, 'w') as f:
                    f.write(html_text)
        else:
            # If there isn't an HTML file, this is that parent Logger object,
            # and it needs to create the main HTML file.
            self.html_file = os.path.join(self.log_dir, name.replace(' ', '_')
                                          + '.html')
            html_text = f"<h1>{self.top_dict['name']} Log</h1>"

            # Write the file.
            with open(self.html_file, 'w') as f:
                f.write(html_text)

    def update_done_time(self):
        """
        Allows the ``top_dict['done_time']`` to be updated before
        :func:`finalize` is called.  This is especially useful for child
        :class:`Logger` objects who might finish their commands before the
        parent finalizes everything.
        """
        self.top_dict['done_time'] = datetime.datetime.now()

    def duration(self):
        """
        Returns the duration from the beginning of the :class:`Logger` object's
        creation until now.

        Returns:
            str:  Duration in the format ``%Hh %Mm %Ss``.
        """
        self.update_done_time()
        dur = self.top_dict['done_time'] - self.top_dict['init_time']
        dur_str = self.strfdelta(dur, "{hrs}h {min}m {sec}s")

        return dur_str

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
        child = Logger(child_name, self.log_dir, tmp_dir=self.tmp_dir,
                       html_file=self.html_file, indent=self.indent+1)
        self.top_dict['log'].append(child)

        return child

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

        abs_new_log_dir = os.path.abspath(new_log_dir)

        # This only gets executed once by the top-level parent Logger object.
        if os.path.exists(self.log_dir):
            copy_tree(self.log_dir, abs_new_log_dir)
            shutil.rmtree(self.log_dir)

        # Change the tmp_dir, html_file, and log_dir for every child Logger
        # recursively.
        self.tmp_dir = os.path.join(abs_new_log_dir,
                                    os.path.relpath(self.tmp_dir,
                                                    self.log_dir))
        self.html_file = os.path.join(abs_new_log_dir,
                                      os.path.relpath(self.html_file,
                                                      self.log_dir))
        self.log_dir = os.path.abspath(new_log_dir)
        for log in self.top_dict['log']:
            if isinstance(log, Logger):
                log.change_log_dir(new_log_dir)

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
        self.top_dict['log'].append(log)

    def log(self, msg, cmd, cwd, live_stdout=False, live_stderr=False,
            return_info=False):
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
            'timestamp': str(start_time),
            'cmd': cmd_str,
            'cmd_id': cmd_id,
            'cwd': str(cwd),
            'return_code': 0,
        }

        # Create & open files for stdout and stderr
        stdout_path = os.path.join(self.tmp_dir, cmd_id + '_stdout')
        stderr_path = os.path.join(self.tmp_dir, cmd_id + '_stderr')

        with open(stdout_path, 'a') as out, open(stderr_path, 'a') as err:
            generator = cf.run_cmd_generator(cmd, cwd)

            if return_info:
                stdout = ''
                stderr = ''

            # Write to stdout/stderr files as text is being returned.
            for result in generator:
                if result['stdout'] is not None:
                    if live_stdout:
                        print(result['stdout'], end='')
                    if return_info:
                        # Generally, '\r' characters aren't wanted here
                        clean_stdout = re.sub('\r', '', result['stdout'])
                        stdout += clean_stdout
                    out.write(result['stdout'])

                elif result['stderr'] is not None:
                    if live_stderr:
                        print(result['stderr'], end='', file=sys.stderr)
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
        self.top_dict['log'].append(log)

        if return_info:
            return {'return_code': log['return_code'], 'stdout': stdout,
                    'stderr': stderr}
        else:
            return {'return_code': log['return_code'], 'stdout': None,
                    'stderr': None}

    def finalize(self):
        """
        This method iterates through each entry in this :class:`Logger`
        object's log list and appends corresponding HTML text to the main HTML
        file. For each entry, the ``stdout``/``stderr`` are copied from their
        respective files in the ``tmp_dir``, and then the ``tmp_dir`` files are
        removed.
        """

        for log in self.top_dict['log']:
            # Each indent is 2 spaces
            i = self.indent * 2

            # Child Logger
            # ------------
            if isinstance(log, Logger):
                # Get the duration of this Logger's commands
                duration = self.duration()

                # First print the header text.
                html_str = (
                    ' '*i + "\n<br>\n" +
                    ' '*i + "<details>\n" +
                    ' '*i + "  <summary>\n" +
                    ' '*i + "    <b><font " +
                    f"size='6'>{log.top_dict['name']}</font></b>\n" +
                    ' '*i + f"    <br>Duration: {duration}\n" +
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
            stdout_path = os.path.join(self.tmp_dir, cmd_id + '_stdout')
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
            stderr_path = os.path.join(self.tmp_dir, cmd_id + '_stderr')
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
        if self.indent == 0:  # Parent
            # Save everything to a JSON file
            json_file = self.top_dict['name'].replace(' ', '_') + '.json'
            json_file = os.path.join(self.log_dir, json_file)

            with open(json_file, 'w') as jf:
                json.dump(self, jf, cls=LoggerEncoder)
