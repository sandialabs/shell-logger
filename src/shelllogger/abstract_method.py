#!/usr/bin/env python3

import inspect


class AbstractMethod(NotImplementedError):
    """
    An ``Exception`` denoting an abstract method that is meant to be
    overridden by a subclass.
    """

    def __init__(self):
        """
        Raise a `NotImplementedError`, indicating which method must be
        implemented for the class to be concrete.
        """
        class_name = (
            inspect.stack()[1].frame.f_locals['self'].__class__.__name__
        )
        method_name = inspect.stack()[1].function
        super().__init__(f"`{class_name}` must implement `{method_name}()`.")
