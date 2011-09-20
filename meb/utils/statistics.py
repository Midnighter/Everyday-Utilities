#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
==================
Statistics Helpers
==================

:Author:
    Moritz Emanuel Beber
:Date:
    2011-01-23
:Copyright:
    Copyright(c) 2011 Jacobs University of Bremen. All rights reserved.
:File:
    statistics.py
"""


import numpy

from .mathfuncs import float_almost_equal


def frequency_distribution(observables, bins=30, binwidth=None):
    """
    Takes a number of events and counts the frequency of these events falling into
    either a fixed number of equi-distant bins over the observed range or bins of
    fixed width over the range.

    Parameters
    ----------
    observables : An iterable of numerals.
    bins : The number of equi-distant bins used over the numeric range.
    binwidth : The width of the bins.

    Returns
    -------
    A list of pairs, the first entry is the centre of the bin borders at which
    the frequency of an event is measured, and the second entry is the frequency
    itself.
    """
    if not observables:
        return []
    minimum = min(observables)
    maximum = max(observables)
    if minimum < 0.0 and maximum > 0.0:
        span = float(maximum + abs(minimum))
    else:
# difference is always positive when max and min have the same sign
        span = float(maximum - minimum)
    if binwidth:
        bins = int(numpy.ceil(span / float(binwidth)))
    if not binwidth:
        binwidth = span / float(bins)
    (counts, binning) = numpy.histogram(observables, bins=bins + 1,\
            range=(minimum, maximum + binwidth))
    data = list()
    for k in xrange(len(counts)):
        if counts[k] > 0:
            data.append((binning[k] + binwidth / 2.0, counts[k]))
    return data

def probability_distribution(observables, bins=30, binwidth=None):
    """
    Normalises the observed frequencies by the total number of elements in
    ``observables``.

    Parameters
    ----------
    observables : An iterable of numerals.
    bins : The number of equi-distant bins used over the numeric range.
    binwidth : The width of the bins.

    Returns
    -------
    A frequency distribution that is normalised to unity.

    Notes
    -----
    See also frequency_distribution_.
    """
    if not observables:
        return []
    total = float(len(observables))
    data = frequency_distribution(observables, bins, binwidth)
    return [(pair[0], pair[1] / total) for pair in data]

def probability_bincounts(observables):
    """
    Normalises the observed frequencies by the total number of elements in
    ``observables``.

    Parameters
    ----------
    observables : An iterable of integer numerals.

    Returns
    -------
    A frequency distribution that is normalised to unity.
    """
    if not observables:
        return []
    total = float(len(observables))
    data = numpy.bincount(observables)
    points = list()
    for (i, value) in enumerate(data):
        if value > 0:
            points.append((i, value / total))
    return points

def compute_zscore(observable, random_stats):
    """
    Parameters
    ----------
    observables : numeral
        original observation
    random_stats : iterable
        same observable in randomised versions
    """
    if not random_stats:
        return numpy.nan
    mean = numpy.mean(random_stats)
    std = numpy.std(random_stats)
    nominator = observable - mean
    if nominator == 0.0:
        return nominator
    if std == 0.0:
        if nominator < 0.0:
            return -numpy.inf
        else:
            return numpy.inf
    else:
        return (nominator / std)

