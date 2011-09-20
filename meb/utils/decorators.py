#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
===================
Decorator Functions
===================

:Author:
    Moritz Emanuel Beber
:Date:
    2011-02-17
:Copyright:
    Copyright(c) 2011 Jacobs University of Bremen. All rights reserved.
:File:
    decorators.py
"""


def new_property(func):
    """
    A decorator function for easy property creation.

    Notes
    -----
    The original author of this property function is *runsun pan* who published
    it under the MIT License. For more information and documentation see also
    http://code.activestate.com/recipes/576742/.
    """
    ops = func() or dict()
    name = ops.get("prefix", '_') + func.__name__ # property name
    fget = ops.get("fget", lambda self: getattr(self, name))
    fset = ops.get("fset", lambda self, value: setattr(self, name, value))
#    fdel = ops.get("fdel", lambda self: delattr(self, name))
#    return property(fget=fget, fset=fset, fdel=fdel, doc=ops.get('doc',''))
    return property(fget=fget, fset=fset, doc=ops.get("doc", "get/set method"))

