#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
==================
Network Statistics
==================

:Author:
    Moritz Emanuel Beber
:Date:
    2011-01-20
:Copyright:
    Copyright(c) 2011 Jacobs University of Bremen. All rights reserved.
:File:
    statistics.py
"""


import randomisation
import numpy
import networkx as nx


def degree_correlation_coefficient(graph):
    """
    Parameters
    ----------
    graph : A graph instance whose interface should resemble a ``networkx.DiGraph``.

    Returns
    -------
    A pearson-like correlation coefficient that ranges from ``-1`` to ``1``.

    Notes
    -----
    For directed graphs only.
    """
    power = numpy.power

    def _undirected_correlation(graph):
        # sum over j*k
        multi_sum = 0.0
        # (sum over j + k)^2
        squared_sum = 0.0
        # sum over j^2 + k^2
        denominator_sum = 0.0
        degree = graph.degree()
        for (u, v) in graph.edges_iter():
            src_degree = float(degree[u])
            tar_degree = float(degree[v])
            multi_sum += src_degree * tar_degree
            denominator_sum += power(src_degree, 2) + power(tar_degree, 2)
            squared_sum += src_degree + tar_degree
        # normalised by a small factor and the number of edges
        squared_sum = power(squared_sum, 2) / float(graph.size() * 4)
        return (multi_sum - squared_sum) / ((denominator_sum / 2.0) - squared_sum)

    def _directed_correlation(graph):
        # sum over j*k
        multi_sum = 0.0
        # (sum over j + k)^2
        squared_sum = 0.0
        # sum over j^2 + k^2
        denominator_sum = 0.0
        in_degree = graph.in_degree()
        out_degree = graph.out_degree()
        for (u, nbrs) in graph.adjacency_iter():
            for v in nbrs:
                src_degree = float(out_degree[u])
                tar_degree = float(in_degree[v])
                multi_sum += src_degree * tar_degree
                denominator_sum += power(src_degree, 2) + power(tar_degree, 2)
                squared_sum += src_degree + tar_degree
        # normalised by a small factor and the number of edges
        squared_sum = power(squared_sum, 2) / float(graph.size() * 4)
        return (multi_sum - squared_sum) / (0.5 * denominator_sum - squared_sum)

    if graph.is_directed():
        return _directed_correlation(graph)
    else:
        return _undirected_correlation(graph)

