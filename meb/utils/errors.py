#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
==========
Exceptions
==========

:Author:
    Moritz Emanuel Beber
:Date:
    2011-02-17
:Copyright:
    Copyright(c) 2011 Jacobs University of Bremen. All rights reserved.
:File:
    errors.py
"""


import errno


class UtilsError(StandardError):
    """
    Error class that is meant to be raised when the arguments provided to a
    function are incorrect.
    """

    def __init__(self, msg, *args, **kw_args):
        """
        Parameters
        ----------
        msg : An unformatted string, i.e., it may contain multiple string
                format markers.

        Returns
        -------
        An ArgumentError instance.

        Notes
        -----
        A variable number of arguments may be passed. They will all be used to
        format msg. So take care that the number and type of additional
        arguments matches the format markers in msg.

        Examples
        --------
        >>> err = errors.ArgumentError("It's too %s outside!", "rainy")
        >>> print(err)
        It's too rainy outside!
        >>> print(err.errno)
        22

        """
        StandardError.__init__(self, *args, **kw_args)
        self.args = (msg,) + args
        self.errno = errno.EINVAL
        self.strerror = msg % args

    def __str__(self):
        """
        Returns
        -------
        strerror : Simply returns the formatted string.
        """
        return self.strerror


class ArgumentError(StandardError):
    """
    Error class that is meant to be raised when the arguments provided to a
    function are incorrect.
    """

    def __init__(self, msg, *args, **kw_args):
        """
        Parameters
        ----------
        msg : An unformatted string, i.e., it may contain multiple string
                format markers.

        Returns
        -------
        An ArgumentError instance.

        Notes
        -----
        A variable number of arguments may be passed. They will all be used to
        format msg. So take care that the number and type of additional
        arguments matches the format markers in msg.

        Examples
        --------
        >>> err = errors.ArgumentError("It's too %s outside!", "rainy")
        >>> print(err)
        It's too rainy outside!
        >>> print(err.errno)
        22

        """
        StandardError.__init__(self, *args, **kw_args)
        self.args = (msg,) + args
        self.errno = errno.EINVAL
        self.strerror = msg % args

    def __str__(self):
        """
        Returns
        -------
        strerror : Simply returns the formatted string.
        """
        return self.strerror


class NetworkError(StandardError):
    """
    Error class that is meant to be raised when an error occured with a network
    connection.
    """
    def __init__(self, msg, *args, **kw_args):
        """
        Parameters
        ----------
        msg : An unformatted string, i.e., it may contain multiple string
                format markers.

        Returns
        -------
        An NetworkError instance.

        Notes
        -----
        A variable number of arguments may be passed. They will all be used to
        format msg. So take care that the number and type of additional
        arguments matches the format markers in msg.

        Examples
        --------
        >>> msg = "The connection to the outside world failed! %d %%"
        >>> err = errors.NetworkError(msg, 0)
        >>> print(err)
        The connection to the outside world failed! 0 %
        >>> print(err.errno)
        121

        """
        StandardError.__init__(self, *args, **kw_args)
        self.args = (msg,) + args
        self.errno = errno.EREMOTEIO
        self.strerror = msg % args

    def __str__(self):
        """
        Returns
        -------
        strerror : Simply returns the formatted string.
        """
        return self.strerror

