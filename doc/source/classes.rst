Helper Classes
==============

The following are a number of helper classes used by :class:`ShellLogger`.

JSON Serialization
------------------

.. autoclass:: shelllogger.ShellLoggerDecoder
   :noindex:

.. todo::

   Figure out why the documentation below is pulling in the docstring for the
   base class as well.

.. autoclass:: shelllogger.ShellLoggerEncoder
   :noindex:

Trace
-----

.. autoclass:: shelllogger.classes.Trace
   :noindex:

.. automethod:: shelllogger.classes::trace_collector
   :noindex:

Strace
~~~~~~

.. autoclass:: shelllogger.ShellLogger.Strace
   :noindex:

Ltrace
~~~~~~

.. autoclass:: shelllogger.ShellLogger.Ltrace
   :noindex:

StatsCollector
--------------

.. autoclass:: shelllogger.classes.StatsCollector
   :noindex:

.. automethod:: shelllogger.classes::stats_collectors
   :noindex:

DiskStatsCollector
~~~~~~~~~~~~~~~~~~

.. autoclass:: shelllogger.ShellLogger.DiskStatsCollector
   :noindex:

CPUStatsCollector
~~~~~~~~~~~~~~~~~

.. autoclass:: shelllogger.ShellLogger.CPUStatsCollector
   :noindex:

MemoryStatsCollector
~~~~~~~~~~~~~~~~~~~~

.. autoclass:: shelllogger.ShellLogger.MemoryStatsCollector
   :noindex:

AbstractMethod
--------------
.. autoexception:: shelllogger.classes.AbstractMethod
   :noindex:
