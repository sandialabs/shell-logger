shelllogger
===========

.. toctree::
   :hidden:
   :maxdepth: 3
   :caption: Contents

   ShellLogger
   classes
   util
   todo

The ``shelllogger`` module allows you to interact with the shell, while logging
various metadata, statistics, and trace information.  Any time you're tempted
to write your own wrapper around things like :class:`subprocess.Popen` or
:func:`subprocess.run`, consider using :func:`ShellLogger.log` instead.  The
following talk from the `US-RSE Virtual Workshop 2021
<https://us-rse.org/virtual-workshop-2021/>`_ illustrates ``shelllogger`` 's
functionality.

.. raw:: html

    <div style="position: relative;
                padding-bottom: 56.25%;
                height: 0;
                overflow: hidden;
                max-width: 100%;
                height: auto;">
        <iframe src="https://www.youtube.com/embed/P32RYY_2V7w?start=5985"
                frameborder="0"
                allowfullscreen
                style="position: absolute;
                       top: 0;
                       left: 0;
                       width: 100%;
                       height: 100%;
                       padding: 10px;">
        </iframe>
    </div>

Where to Get shelllogger
------------------------

The source repository for this module can be found `here
<https://internal.gitlab.server/ShellLogger/ShellLogger>`_.  See the project's
`README.md
<https://internal.gitlab.server/ShellLogger/ShellLogger/-/blob/master/README.md>`_
for details on how to clone, install, and otherwise interact with the project.

Using shelllogger
-----------------

At a high-level, :func:`ShellLogger.log` allows you to execute commands, given
as strings, in the shell.  When a command is executed, :class:`ShellLogger`
will also collect the following information:

* The command run
* A description of the command, or why it was run
* ``stdout`` and ``stderr``
* Environment variables
* Working directory
* Hostname
* User and group
* Umask
* Return code
* Ulimit
* Command start/stop time and duration

It can also optionally collect:

* Resource usage (CPU, memory, disk)
* Trace information (``strace``, ``ltrace``)

These data are collected in a "log book".  When you call
:func:`ShellLogger.finalize`, the contents of the log book are written to a
HTML log file.

Example
^^^^^^^

.. todo::

   Insert simplest example here, and link to other examples in the repo.

For more detailed usage information, see the :doc:`ShellLogger`.
