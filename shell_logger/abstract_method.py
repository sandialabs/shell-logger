"""Provides the :class:`AbstractMethod` exception."""

# © 2023 National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the
# U.S. Government retains certain rights in this software.

# SPDX-License-Identifier: BSD-3-Clause

import inspect


class AbstractMethod(NotImplementedError):
    """
    An abstract method meant to be overridden.

    An ``Exception`` denoting an abstract method that is meant to be
    overridden by a subclass.
    """

    def __init__(self):
        """
        Raise a ``NotImplementedError``.

        Indicate which method must be implemented for the class to be
        concrete.
        """
        class_name = (
            inspect.stack()[1].frame.f_locals["self"].__class__.__name__
        )
        method_name = inspect.stack()[1].function
        super().__init__(f"`{class_name}` must implement `{method_name}()`.")
