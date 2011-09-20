#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
==================
Network Classes
==================

:Author:
    Moritz Emanuel Beber
:Date:
    2011-06-01
:Copyright:
    Copyright(c) 2011 Jacobs University of Bremen. All rights reserved.
:File:
    classes.py
"""


import itertools
import networkx as nx
import numpy


class BipartiteGraph(nx.Graph):
    """
    """

    def __init__(self, name="", *args, **kw_args):
        """
        """
        nx.Graph.__init__(self, name=name)

    def _project(self, nbunch, unipartite):
        unipartite.add_nodes_from(nbunch)
        for n in nbunch:
            unipartite.add_edges_from(itertools.combinations(self.adj[n], 2))

    def project2top(self, multi=False):
        if multi:
            unipartite = nx.MultiGraph(name=self.name + " projection")
        else:
            unipartite = nx.Graph(name=self.name + " projection")
        self._project([n for n in self if self.node[n]["pop"] == -1], unipartite)
        return unipartite

    def project2bottom(self, multi=False):
        if multi:
            unipartite = nx.MultiGraph(name=self.name + " projection")
        else:
            unipartite = nx.Graph(name=self.name + " projection")
        self._project([n for n in self if self.node[n]["pop"] == 1], unipartite)
        return unipartite


class BipartiteDiGraph(nx.DiGraph):
    """
    """

    def __init__(self, name="", *args, **kw_args):
        """
        """
        nx.DiGraph.__init__(self, name=name)

    def _project(self, nbunch, unipartite):
        unipartite.add_nodes_from(nbunch)
        for n in nbunch:
            unipartite.add_edges_from((u, v) for u in self.pred[n] for v in
                    self.succ[n] if u != v)

    def project2top(self, multi=False):
        if multi:
            unipartite = nx.MultiDiGraph(name=self.name + " projection")
        else:
            unipartite = nx.DiGraph(name=self.name + " projection")
        self._project([n for n in self if self.node[n]["pop"] == -1], unipartite)
        return unipartite

    def project2bottom(self, multi=False):
        if multi:
            unipartite = nx.MultiDiGraph(name=self.name + " projection")
        else:
            unipartite = nx.DiGraph(name=self.name + " projection")
        self._project([n for n in self if self.node[n]["pop"] == 1], unipartite)
        return unipartite

