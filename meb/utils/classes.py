#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
===============
Utility Classes
===============

:Author:
    Moritz Emanuel Beber
:Date:
    2011-02-17
:Copyright:
    Copyright(c) 2011 Jacobs University of Bremen. All rights reserved.
:File:
    classes.py

Notes
-----
Most classes (unless they inherit from old-style classes) are new-style classes.
Attributes and methods not intended to be accessed directly by the user are
preceeded by a single underscore '_' but they can be used if the user knows
what he is doing. Those preceeded with two underscores '__' should under no
circumstances be touched.
"""


import logging
import logging.handlers
import urllib2
import re

from .singletonmixin import Singleton


class BasicOptionsManager(Singleton):
    """
    A basic setup for a class that manages and unifies certain options.

    Notes
    -----
    BasicOptionsManager mainly handles logging of information. Subclasses may
    add more options to that.
    """

    def __init__(self, *args, **kw_args):
        """
        Sets up some variables to ease logging.
        """
        Singleton.__init__(self, *args, **kw_args)
        self._log_levels = {"debug": logging.DEBUG, "info": logging.INFO,
            "warning": logging.WARNING, "error": logging.ERROR,
            "critical": logging.CRITICAL}
        self.logger = logging.getLogger("")
        self._log_level = logging.WARNING
        self.logger.setLevel(logging.DEBUG)
        self._handler = logging.StreamHandler()
        self._handler.setLevel(self._log_level)
        self._formatter = logging.Formatter("%(name)s - %(levelname)s - "\
                "%(message)s")
        self._handler.setFormatter(self._formatter)
        self.logger.addHandler(self._handler)

    def change_handler(self, handler):
        """
        Parameters
        ----------
        handler : A valid ``logging.handler`` instance. It is used to replace
        the default ``StreamHandler`` instance.
        """
        self.logger.removeHandler(self._handler)
        self._handler = handler
        self._handler.setFormatter(self._formatter)
        self._handler.setLevel(self._log_level)
        self.logger.addHandler(self._handler)

    def change_log_level(self, level):
        """
        Parameters
        ----------
        level : A string that identifies one of the logging levels. Subclasses
        may add more distinctive identifiers to the dictionary.
        """
        self._log_level = self._log_levels[level]
        self._handler.setLevel(self._log_level)


class CLAMVParser(object):
    """
    A parser for the website detailing available hosts on the CLAMV. Intended for
    Jacobs University internal use only.
    """
    def __init__(self, url="http://www.clamv.jacobs-university.de/CLAMV/"\
            "Wizard/Accounting/html/CLAMVCluster.html", *args, **kw_args):
        """
        Parameters
        ----------
        url : A url whose content should be parsed.

        Notes
        -----
        ``urlopen`` may raise an exception.
        """
        object.__init__(self)
        self.url = url
        self.content = urllib2.urlopen(self.url).readlines()

    def get_hosts(self):
        """
        Uses regular expressions in order to parse relevant sections of the
        website.

        Returns
        -------
        A list of available hosts whose number of free cpus is greater than
        zero.
        """
        pattern = re.compile(r"""
            <td>(tlab\d+|munch\d+)</td>
            <td>(\d+)</td>
            <td>(\d+\.\d+)</td>
            <td>(\d+\.\d+)</td>
            """, re.I | re.X)
        hosts = list()
        for line in self.content:
            mobj = pattern.search(line)
            if mobj:
                cpus = int(mobj.group(2))
                if cpus > 0:
                    hosts.append("%s.clamv.jacobs-university.de"\
                        % mobj.group(1))
            else:
                continue
        # hosts 32 to 35 are removed because their setup is strange and many
        # programs won't work on them.
        for i in xrange(32,36):
            host = "tlab0%d.clamv.jacobs-university.de" % i
            try:
                hosts.remove(host)
            except ValueError:
                continue
        return hosts

