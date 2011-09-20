#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
=========================
Plot Interface to GGPlot2
=========================

:Author:
    Moritz Emanuel Beber
:Date:
    2010-11-30
:Copyright:
    Copyright(c) 2010 Jacobs University of Bremen. All rights reserved.
:File:
    plots.py
"""


import rpy2.robjects as r_objects
import rpy2.rinterface as ri
import rpy2.robjects.lib.ggplot2 as ggplot2

from rpy2.rinterface import RRuntimeError
from rpy2.robjects.packages import importr


class GGPlot(object):
    """
    A python interface to ggplot2 using the rpy2 interface to R. Aims to make
    plotting easily accessible. After initialisation of the plot, further
    ggplot2 layers can be added to the plot.
    """

    def __init__(self, data_frame, drawing_format, filename=None, width=None,\
            height=None, *args, **kw_args):
        """
        Initialises the basic ggplot.

        Parameters
        ----------
        data_frame : ``rpy2.robjects.DataFrame``
        drawing_format : A string identifying the output format (platform
        dependent, may include x11, pdf, png)
        filename : The full path of the output file without a file format
        extension.
        width : Numeric width of the plot, the unit depends on the drawing
        format.
        height : Numeric height of the plot, the unit depends on the drawing
        format.
        """
        object.__init__(self)
        assert ri.initr() == 0, "Error during initialisation of R!"
        self._drawing_format = drawing_format.lower()
        self._gr_devices = importr("grDevices")
        if drawing_format in self._gr_devices.deviceIsInteractive() or\
                drawing_format.upper() in self._gr_devices.deviceIsInteractive():
            self._filename = None
            if width and height:
                eval("self._gr_devices.%s(width=width, height=height)" %\
                        self._drawing_format)
            else:
                eval("self._gr_devices.%s()" % self._drawing_format)
        else:
            self._filename = "%s.%s" % (filename, self._drawing_format)
            if width and height:
                eval("self._gr_devices.%s(file=self._filename, width=width,"\
                        "height=height)" %\
                        self._drawing_format)
            else:
                eval("self._gr_devices.%s(file=self._filename)" %\
                        self._drawing_format)
        self._dev_id = self._gr_devices.dev_cur()[0]
        self.data_frame = data_frame
        self.plot = ggplot2.ggplot(self.data_frame)

    def __del__(self):
        """
        Turn off the plotting device and ask for confirmation in case the device
        is interactive.
        """
        dev_list = self._gr_devices.dev_list()
        if bool(dev_list):
            if self._dev_id in self._gr_devices.dev_list():
                if self._gr_devices.dev_interactive()[0]:
                    raw_input("press Enter")
                self._gr_devices.dev_off(self._dev_id)

    def __nonzero__(self):
        return bool(self.plot)

    def __add__(self, other):
        return self.plot + other

    def __radd__(self, other):
        return self.plot + other

    def __iadd__(self, other):
        self.plot += other
        return self

    def show(self):
        """
        Display changes made to the plot by redrawing to the device.
        """
        if self.plot:
            try:
                assert self._gr_devices.dev_set(self._dev_id)[0] ==\
                        self._dev_id,\
                        "Cannot make the device %d the currently active one!"\
                        % self._dev_id
                self.plot.plot()
            except RRuntimeError as err:
                print err

    def _make_axis_format(self, name, limits, breaks):
        """
        """
        kw_args = dict()
        kw_args["name"] = name
        if limits:
            kw_args["limits"] = ri.FloatSexpVector(limits)
        if breaks:
            kw_args["breaks"] = ri.FloatSexpVector(breaks)
        return kw_args

    def format_x_axis(self, name, limits=None, breaks=None):
        """
        """
        kw_args = self._make_axis_format(name, limits, breaks)
        self.plot += ggplot2.scale_x_continuous(**kw_args)

    def format_y_axis(self, name, limits=None, breaks=None):
        """
        """
        kw_args = self._make_axis_format(name, limits, breaks)
        self.plot += ggplot2.scale_y_continuous(**kw_args)

