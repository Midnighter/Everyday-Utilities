#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
======================
Mathematical Functions
======================

:Author:
    Moritz Emanuel Beber
:Date:
    2011-01-25
:Copyright:
    Copyright(c) 2011 Jacobs University of Bremen. All rights reserved.
:File:
    mathfuncs.py
"""


import sys
import numpy

from .errors import UtilsError


def binomial_coefficient(n, k):
    """
    n! / ((n - k)! * k!)
    """
    if 0 <= k <= n:
        return reduce(lambda a, b: a * (n - b) / (b + 1), xrange(k), 1)
    else:
        return 0

def binomial_coefficient2(n, k):
    """
    n! / ((n - k)! * k!)

    Author : Jussi Piitulainen
             <http://www.velocityreviews.com/forums/
             t502438-combination-function-in-python.html>
    """
    if 0 <= k <= n:
        p = 1
        for t in xrange(min(k, n - k)):
            p = (p * (n - t)) // (t + 1)
        return p
    else:
        return 0

def binomial_coefficient3(n, k):
    """
    n! / ((n - k)! * k!)

    Author : Anton Vredegoor
             <http://www.velocityreviews.com/forums/
             t502438-combination-function-in-python.html>
    """
    return reduce(lambda a, b: a * (n - b) / (b + 1), xrange(k), 1)

def float_almost_equal(a, b, absolute=sys.float_info.epsilon,
        relative=sys.float_info.dig):
    tests = list()
    if absolute:
        tests.append(abs(absolute))
    if relative:
        tests.append(pow(10, -relative) * abs(a))
    return (abs(a - b) <= max(tests))

def power_method(matrix, threshold=1E-08, max_iter=500):
    """
    Estimates the largest eigenvector and eigenvalue of a square matrix by
    repeated multiplication into a vector.
    """
    dot = numpy.dot
    norm = numpy.linalg.norm

    vec_old = numpy.zeros(len(matrix))
    vec_new = numpy.random.random_sample(len(matrix))
    vec_new /= norm(vec_new)
    for i in xrange(max_iter):
        vec_old = vec_new
        vec_new = dot(matrix.A, vec_old)
        vec_new /= norm(vec_new)
        if abs(vec_new - vec_old).sum() < threshold:
            break
    if i == max_iter:
        raise UtilsError("power method failed to converge in %d iterations" %\
                max_iter)
    # Rayleigh quotient
    q = dot(vec_new, vec_old) / dot(vec_old, vec_old)
    return (q, vec_new)

def norm_uncertain_vector(vector):
    normed = list()
    # find the norm
    summation = numpy.sum([numpy.power(pair[0], 2) for pair in vector])
    norm = numpy.sqrt(summation)
    diff = numpy.power(summation, 1.5)
    for (mean, std) in vector:
        new_mean = mean / norm
        new_std = abs(numpy.reciprocal(norm) - (numpy.power(mean, 2) / diff))\
                * std
        normed.append((new_mean, new_std))
    return normed

