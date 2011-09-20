#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
========================
Python Utilities Package
========================

:Authors:
    Moritz Emanuel Beber
:Date:
    2011-04-12
:Copyright:
    Copyright(c) 2011 Jacobs University of Bremen. All rights reserved.
:File:
    setup.py
"""


from distutils.core import setup


setup(
    name = "meb",
    version = "0.1",
    description = "various utility classes and functions for python",
    author = "Moritz Emanuel Beber",
    author_email = "moritz (dot) beber (at) googlemail (dot) com",
    url = "http://github.com/Midnighter/Everyday-Utilities",
    packages = [
            "meb",
            "meb.utils",
            "meb.utils.network",
            "meb.utils.tests",
            "meb.utils.network.tests"
            ],
    )

