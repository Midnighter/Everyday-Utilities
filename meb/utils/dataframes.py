#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
============
R Dataframes
============

:Author:
    Moritz Emanuel Beber
:Date:
    2010-11-29
:Copyright:
    Copyright(c) 2010 Jacobs University of Bremen. All rights reserved.
:File:
    dataframes.py
"""


import numpy
import rpy2.robjects as r_objects
import rpy2.rinterface as ri
import rpy2.robjects.numpy2ri # automatic shared memory between numpy and R
r_objects.conversion.py2ri = rpy2.robjects.numpy2ri.numpy2ri
r_objects.conversion.ri2numpy = rpy2.robjects.numpy2ri.ri2numpy


from collections import defaultdict


def one_dimensional(observables):
    """
    Parameters
    ----------
    observables : Can be one of the following types of containers
        1. An iterable of shape len(observables) x 1.
        2. A dictionary, in which case keys are taken as labels for the data
           and values are as in 1.
        3. A ``dict`` of ``dict``, allowing for combinations of labels to form
           a 2D facet grid, values are as in 1.

    Returns
    -------
    An rpy2.robjects.DataFrame with one column ``xpos``. Additional columns
    ``label`` and ``label_2`` may be present.
    """
    # collect the observables into a table
    data = defaultdict(list)
    if isinstance(observables, dict):
        for (label, content) in observables.iteritems():
            if isinstance(content, dict):
                for (label_2, real_data) in content.iteritems():
                    data["label"].extend([label] * len(real_data))
                    data["label_2"].extend([label_2] * len(real_data))
                    data["xpos"].extend(real_data)
            else:
                data["label"].extend([label] * len(content))
                data["xpos"].extend(content)
    elif isinstance(observables, list):
        data["xpos"] = observables
    elif isinstance(observables, numpy.array):
        assert observables.shape == (len(observables),)
        data["xpos"] = observables
        return r_objects.DataFrame(data)
    else:
        raise(ValueError("Wrong data container type!"))
    # convert to R-compatible data containers
    if data.has_key("label_2"):
        data["label_2"] = r_objects.FactorVector(data["label_2"])
    if data.has_key("label"):
        data["label"] = r_objects.FactorVector(data["label"])
    data["xpos"] = numpy.array(data["xpos"])
    return r_objects.DataFrame(data)

def two_dimensional(observables):
    """
    Parameters
    ----------
    observables : Can be one of the following types of containers:
        1. An iterable of shape len(observables) x 2.
        2. A dictionary, in which case keys are taken as labels for the data
           and values are as in 1.
        3. A ``dict`` of ``dict``, allowing for combinations of labels to form
           a 2D facet grid, values are as in 1.

    Returns
    -------
    An rpy2.robjects.DataFrame with two columns ``xpos`` and ``ypos``. Additional
    columns ``label`` and ``label_2`` may be present.
    """
    # collect the observables into a table
    data = defaultdict(list)
    if isinstance(observables, dict):
        for (label, content) in observables.iteritems():
            if isinstance(content, dict):
                for (label_2, real_data) in content.iteritems():
                    data["label"].extend([label] * len(real_data))
                    data["label_2"].extend([label_2] * len(real_data))
                    data["xpos"].extend([pair[0] for pair in real_data])
                    data["ypos"].extend([pair[1] for pair in real_data])
            else:
                data["label"].extend([label] * len(content))
                data["xpos"].extend([pair[0] for pair in content])
                data["ypos"].extend([pair[1] for pair in content])
    elif isinstance(observables, list):
        data["xpos"].extend([pair[0] for pair in observables])
        data["ypos"].extend([pair[1] for pair in observables])
    elif isinstance(observables, numpy.array):
        assert observables.shape == (len(observables), 2)
        data["xpos"] = observables[:, 0]
        data["ypos"] = observables[:, 1]
        return r_objects.DataFrame(data)
    else:
        raise(ValueError("Wrong data container type!"))
    # convert to R-compatible data containers
    if data.has_key("label_2"):
        data["label_2"] = r_objects.FactorVector(data["label_2"])
    if data.has_key("label"):
        data["label"] = r_objects.FactorVector(data["label"])
    data["xpos"] = numpy.array(data["xpos"])
    data["ypos"] = numpy.array(data["ypos"])
    return r_objects.DataFrame(data)

def two_dimensional_with_label(observables):
    """
    Parameters
    ----------
    observables : iterable
        An iterable of three tuples.

    Returns
    -------
    An rpy2.robjects.DataFrame with three columns ``xpos``, ``ypos``, and
    ``label``.
    """
    # collect the observables into a table
    data = defaultdict(list)
    if isinstance(observables, list):
        data["xpos"].extend([triple[0] for triple in observables])
        data["ypos"].extend([triple[1] for triple in observables])
        data["label"].extend([triple[2] for triple in observables])
    else:
        raise(ValueError("Wrong data container type!"))
    # convert to R-compatible data containers
    if data.has_key("label"):
        data["label"] = r_objects.FactorVector(data["label"])
    data["xpos"] = numpy.array(data["xpos"])
    data["ypos"] = numpy.array(data["ypos"])
    return r_objects.DataFrame(data)

def two_dimensional_y_uncertainty(observables):
    """
    Parameters
    ----------
    observables : Can be one of the following types of containers:
        1. An iterable of shape len(observables) x 3.
        2. A dictionary, in which case keys are taken as labels for the data
           and values are as in 1.
        3. A ``dict`` of ``dict``, allowing for combinations of labels to form
           a 2D facet grid, values are as in 1.

    Returns
    -------
    An rpy2.robjects.DataFrame with four columns ``xpos``, ``ypos``, ``ymin``,
    and ``ymax``. Additional columns ``label`` and ``label_2`` may be present.
    """
    # collect the observables into a table
    data = defaultdict(list)
    if isinstance(observables, dict):
        for (label, content) in observables.iteritems():
            if isinstance(content, dict):
                for (label_2, real_data) in content.iteritems():
                    data["label"].extend([label] * len(real_data))
                    data["label_2"].extend([label_2] * len(real_data))
                    data["xpos"].extend([triple[0] for triple in real_data])
                    data["ypos"].extend([triple[1] for triple in real_data])
                    data["ymin"].extend([(triple[1] - triple[2])\
                            for triple in real_data])
                    data["ymax"].extend([(triple[1] + triple[2])\
                            for triple in real_data])
            else:
                data["label"].extend([label] * len(content))
                data["xpos"].extend([triple[0] for triple in content])
                data["ypos"].extend([triple[1] for triple in content])
                data["ymin"].extend([(triple[1] - triple[2])\
                        for triple in content])
                data["ymax"].extend([(triple[1] + triple[2])\
                        for triple in content])
    elif isinstance(observables, list):
        data["xpos"].extend([triple[0] for triple in observables])
        data["ypos"].extend([triple[1] for triple in observables])
        data["ymin"].extend([(triple[1] - triple[2])\
                for triple in observables])
        data["ymax"].extend([(triple[1] + triple[2])\
                for triple in observables])
    elif isinstance(observables, numpy.array):
        assert observables.shape == (len(observables), 3)
        data["xpos"] = observables[:, 0]
        data["ypos"] = observables[:, 1]
        data["ymin"] = observables[:, 1] - observables[:, 2]
        data["ymax"] = observables[:, 1] + observables[:, 2]
        return r_objects.DataFrame(data)
    else:
        raise(ValueError("Wrong data container type!"))
    # convert to R-compatible data containers
    if data.has_key("label_2"):
        data["label_2"] = r_objects.FactorVector(data["label_2"])
    if data.has_key("label"):
        data["label"] = r_objects.FactorVector(data["label"])
    data["xpos"] = numpy.array(data["xpos"])
    data["ypos"] = numpy.array(data["ypos"])
    data["ymin"] = numpy.array(data["ymin"])
    data["ymax"] = numpy.array(data["ymax"])
    return r_objects.DataFrame(data)

def three_dimensional(observables):
    """
    Parameters
    ----------
    observables : Can be one of the following types of containers:
        1. An iterable of shape len(observables) x 3.
        2. A dictionary, in which case keys are taken as labels for the data
           and values are as in 1.
        3. A ``dict`` of ``dict``, allowing for combinations of labels to form
           a 2D facet grid, values are as in 1.

    Returns
    -------
    An rpy2.robjects.DataFrame with three columns ``xpos``, ``ypos``, and
    ``zpos``. Additional columns ``label`` and ``label_2`` may be present.
    """
    # collect the observables into a table
    data = defaultdict(list)
    if isinstance(observables, dict):
        for (label, content) in observables.iteritems():
            if isinstance(content, dict):
                for (label_2, real_data) in content.iteritems():
                    data["label"].extend([label] * len(real_data))
                    data["label_2"].extend([label_2] * len(real_data))
                    data["xpos"].extend([triple[0] for triple in real_data])
                    data["ypos"].extend([triple[1] for triple in real_data])
                    data["zpos"].extend([triple[2] for triple in real_data])
            else:
                data["label"].extend([label] * len(content))
                data["xpos"].extend([triple[0] for triple in content])
                data["ypos"].extend([triple[1] for triple in content])
                data["zpos"].extend([triple[2] for triple in content])
    elif isinstance(observables, list):
        data["xpos"].extend([triple[0] for triple in observables])
        data["ypos"].extend([triple[1] for triple in observables])
        data["zpos"].extend([triple[2] for triple in observables])
    elif isinstance(observables, numpy.array):
        assert observables.shape == (len(observables), 3)
        data["xpos"] = observables[:, 0]
        data["ypos"] = observables[:, 1]
        data["zpos"] = observables[:, 2]
        return r_objects.DataFrame(data)
    else:
        raise(ValueError("Wrong data container type!"))
    # convert to R-compatible data containers
    if data.has_key("label_2"):
        data["label_2"] = r_objects.FactorVector(data["label_2"])
    if data.has_key("label"):
        data["label"] = r_objects.FactorVector(data["label"])
    data["xpos"] = numpy.array(data["xpos"])
    data["ypos"] = numpy.array(data["ypos"])
    data["zpos"] = numpy.array(data["zpos"])
    return r_objects.DataFrame(data)

def three_dimensional_with_label(observables):
    """
    Parameters
    ----------
    observables : iterable
        An iterable of four tuples.

    Returns
    -------
    An rpy2.robjects.DataFrame with three columns ``xpos``, ``ypos``, ``zpos``,
    and ``label``.
    """
    # collect the observables into a table
    data = defaultdict(list)
    if isinstance(observables, list):
        data["xpos"].extend([triple[0] for triple in observables])
        data["ypos"].extend([triple[1] for triple in observables])
        data["zpos"].extend([triple[2] for triple in observables])
        data["label"].extend([triple[3] for triple in observables])
    else:
        raise(ValueError("Wrong data container type!"))
    # convert to R-compatible data containers
    if data.has_key("label"):
        data["label"] = r_objects.FactorVector(data["label"])
    data["xpos"] = numpy.array(data["xpos"])
    data["ypos"] = numpy.array(data["ypos"])
    data["zpos"] = numpy.array(data["zpos"])
    return r_objects.DataFrame(data)

def three_dimensional_y_uncertainty(observables):
    """
    Parameters
    ----------
    observables : Can be one of the following types of containers:
        1. An iterable of shape len(observables) x 4. The expected format is
           x, y, std(y), z.
        2. A dictionary, in which case keys are taken as labels for the data
           and values are as in 1.
        3. A ``dict`` of ``dict``, allowing for combinations of labels to form
           a 2D facet grid, values are as in 1.

    Returns
    -------
    An rpy2.robjects.DataFrame with five columns ``xpos``, ``ypos``, ''ymin'',
    ''ymax'', and ``zpos``. Additional columns ``label`` and ``label_2`` may be
    present.
    """
    # collect the observables into a table
    data = defaultdict(list)
    if isinstance(observables, dict):
        for (label, content) in observables.iteritems():
            if isinstance(content, dict):
                for (label_2, real_data) in content.iteritems():
                    data["label"].extend([label] * len(real_data))
                    data["label_2"].extend([label_2] * len(real_data))
                    data["xpos"].extend([triple[0] for triple in real_data])
                    data["ypos"].extend([triple[1] for triple in real_data])
                    data["ymin"].extend([(triple[1] - triple[2])\
                            for triple in real_data])
                    data["ymax"].extend([(triple[1] + triple[2])\
                            for triple in real_data])
                    data["zpos"].extend([triple[3] for triple in real_data])
            else:
                data["label"].extend([label] * len(content))
                data["xpos"].extend([triple[0] for triple in content])
                data["ypos"].extend([triple[1] for triple in content])
                data["ymin"].extend([(triple[1] - triple[2])\
                        for triple in content])
                data["ymax"].extend([(triple[1] + triple[2])\
                        for triple in content])
                data["zpos"].extend([triple[3] for triple in content])
    elif isinstance(observables, list):
        data["xpos"].extend([triple[0] for triple in observables])
        data["ypos"].extend([triple[1] for triple in observables])
        data["ymin"].extend([(triple[1] - triple[2])\
                for triple in observables])
        data["ymax"].extend([(triple[1] + triple[2])\
                for triple in observables])
        data["zpos"].extend([triple[3] for triple in observables])
    elif isinstance(observables, numpy.array):
        assert observables.shape == (len(observables), 4)
        data["xpos"] = observables[:, 0]
        data["ypos"] = observables[:, 1]
        data["ymin"] = observables[:, 1] - observables[:, 2]
        data["ymax"] = observables[:, 1] + observables[:, 2]
        data["zpos"] = observables[:, 3]
        return r_objects.DataFrame(data)
    else:
        raise(ValueError("Wrong data container type!"))
    # convert to R-compatible data containers
    if data.has_key("label_2"):
        data["label_2"] = r_objects.FactorVector(data["label_2"])
    if data.has_key("label"):
        data["label"] = r_objects.FactorVector(data["label"])
    data["xpos"] = numpy.array(data["xpos"])
    data["ypos"] = numpy.array(data["ypos"])
    data["ymin"] = numpy.array(data["ymin"])
    data["ymax"] = numpy.array(data["ymax"])
    data["zpos"] = numpy.array(data["zpos"])
    return r_objects.DataFrame(data)

