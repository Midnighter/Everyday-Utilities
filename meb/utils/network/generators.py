#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
==================
Network Generators
==================

:Author:
    Moritz Emanuel Beber
:Date:
    2011-03-10
:Copyright:
    Copyright(c) 2011 Jacobs University of Bremen. All rights reserved.
:File:
    generators.py
"""


from . import classes
import warnings
import numpy


def rbp_network(top, bottom, p, directed=False, seed=None):
    """
    Creates a random bipartite graph with a link probability according to the
    principles of an Erdos-Renyi-like random graph.

    Parameters
    ----------
    top: int or iter
        The number of or a sequence of one population of nodes.
    bottom: int or iter
        The number of or a sequence of the other population of nodes.
    p: float
        The probability of a link being present.
    directed: bool (optional)
        Whether the generated network should be directed or undirected.
    seed: int (optional)
        Define a fixed seed for the random number generator, for repeatable
        experiments.

    Returns
    -------
    A networkx.Graph or networkx.DiGraph object. The two populations of nodes
    are recorded in the graph attributes under the keys: "top" and "bottom".
    """
    if seed:
        numpy.random.seed(seed)
    if hasattr(top, "__iter__"):
        top = set(top)
    else:
        top = range(int(top))
    if hasattr(bottom, "__iter__"):
        bottom = set(bottom)
    else:
        bottom = range(len(top), len(top) + int(bottom))
    if directed:
        network = classes.BipartiteDiGraph(name="rbp directed graph")
    else:
        network = classes.BipartiteGraph(name="rbp undirected graph")
    network.add_nodes_from(top, pop=1)
    network.add_nodes_from(bottom, pop=-1)
    uniform = numpy.random.random_sample
    for tar in top:
        for src in bottom:
            if uniform() < p:
                network.add_edge(src, tar)
    if directed:
        for tar in bottom:
            for src in top:
                if uniform() < p:
                    network.add_edge(src, tar)
    return network

