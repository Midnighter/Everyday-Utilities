#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
=======================
Multiprocessing Classes
=======================

:Author:
    Moritz Emanuel Beber
:Date:
    2011-02-27
:Copyright:
    Copyright(c) 2011 Jacobs University of Bremen. All rights reserved.
:File:
    parallel.py

Notes
-----
Most classes (unless they inherit from old-style classes) are new-style classes.
Attributes and methods not intended to be accessed directly by the user are
preceeded by a single underscore '_' but they can be used if the user knows
what he is doing. Those preceeded with two underscores '__' should under no
circumstances be touched.
"""


import multiprocessing


class ProcessPoolWorker(multiprocessing.Process):
    """
    Worker thread that operates on items from its queue.
    """

    def __init__(self, queue, exception_queue=None):
        """
        """
        multiprocessing.Process.__init__(self)
        self._queue = queue
        self._exception_queue = exception_queue
        self.daemon = True

    def run(self):
        """
        """
        while True:
            (perform, args, kw_args) = self._queue.get()
            try:
                perform(*args, **kw_args)
            except StandardError as err:
                if self._exception_queue:
                    self._exception_queue.put((err, perform, args, kw_args))
            finally:
                self._queue.task_done()


def ProcessPool(object):
    """
    """

    def __init__(self, num_processes=multiprocessing.cpu_count(), retry=False):
        """
        """
        object.__init__(self)
        self.queue = multiprocessing.JoinableQueue()
        if retry:
            self.exception_queue = multiprocessing.JoinableQueue()
        else:
            self.exception_queue = None
        for i in xrange(num_processes):
            w = ProcessPoolWorker(self.queue, self.exception_queue)
            w.start()

    def put(self, perform, *args, **kw_args):
        """
        """
        self.queue.put((perform, args, kw_args))

