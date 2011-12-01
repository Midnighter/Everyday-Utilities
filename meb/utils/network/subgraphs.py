#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
===================
Subgraph Statistics
===================

:Author:
    Moritz Emanuel Beber
:Date:
    2011-05-27
:Copyright:
    Copyright(c) 2011 Jacobs University of Bremen. All rights reserved.
:File:
    subgraphs.py
"""


import itertools
import numpy
import networkx as nx

from .. import statistics as stats
from . import randomisation as net_rnd

mtf_sz3_id2num = {6: 1, 36: 2, 12: 3, 74: 4, 14: 5, 78: 6, 38: 7, 98: 8,
        108: 9, 46: 10, 102: 11, 110: 12, 238: 13}
mtf_sz3_num2id = {1: 6, 2: 36, 3: 12, 4: 74, 5: 14, 6: 78, 7: 38, 8: 98,
        9: 108, 10: 46, 11: 102, 12: 110, 13: 238}
tricode2id = {"021D": 6, "021U": 36, "021C": 12, "111D": 74, "111U": 14, "030T":
        38, "030C": 98, "201": 78, "120D": 108, "120U": 46, "120C": 102,
        "210":110, "300": 238}
tricode2num = {"021D": 1, "021U": 2, "021C": 3, "111D": 4, "111U": 5, "030T":
        7, "030C": 8, "201": 6, "120D": 9, "120U": 10, "120C": 11,
        "210": 12, "300": 13}
num2tricode = {1: "021D", 2: "021U", 3: "021C", 4: "111D", 5: "111U", 7: "030T",
        8: "030C", 6: "201", 9: "120D", 10: "120U", 11: "120C",
        12: "210", 13: "300"}


def compute_triad_zscores(network, census="mtf_counts", randoms="randoms",
        mapping=num2tricode):
    zscores = numpy.zeros(13)
    for mtf_num in xrange(1, 14):
        mtf = mapping[mtf_num]
        zscores[mtf_num - 1] = stats.compute_zscore(
                network.graph[census].get(mtf, 0.0),
                [rnd.graph[census].get(mtf, 0.0) for rnd in\
                    network.graph[randoms]])
    return zscores

def generate_random_ensemble(args):
    template = args[0]
    i = args[1]
    if len(args) > 2:
        switches = args[2]
    else:
        switches = 100
    rewire = net_rnd.NetworkRewiring()
    (rnd, success) = rewire.randomise(template, flip=switches)
    rnd.graph["mtf_counts"] = triadic_census(rnd)
    print "randomised network", i, "switching success", success
    return rnd


################################################################################
#    (C) Reya Group: http://www.reyagroup.com
#    Alex Levenson (alex@isnotinvain.com)
#    Diederik van Liere (diederik.vanliere@rotman.utoronto.ca)
#    BSD license.
################################################################################

triad_names = ("003", "012", "102", "021D","021U", "021C", "111D", "111U",
        "030T", "030C", "201", "120D","120U", "120C", "210", "300")
tricodes = (1, 2, 2, 3, 2, 4, 6, 8, 2, 6, 5, 7, 3, 8, 7, 11, 2, 6, 4, 8, 5, 9,
        9, 13, 6, 10, 9, 14, 7, 14, 12, 15, 2, 5, 6, 7, 6, 9, 10, 14, 4, 9, 9,
        12, 8, 13, 14, 15, 3, 7, 8, 11, 7, 12, 14, 15, 8, 14, 13, 15, 11, 15,
        15, 16)
tricode_to_name = dict((i, triad_names[tricodes[i] - 1])\
        for i in range(len(tricodes))) # for Python 3.x compatibility

def triadic_census(graph, m=None, count_disconnected=False, record_triads=False):
    """
    Counts all directed triads (three-node subgraphs).

    Triadic census is a count of how many of the 16 possible types of triad are
    present in a graph (13 connected and 3 less connected ones).

    Parameters
    ----------
    graph : directed graph
        A directed graph whose nodes are integers from 0 to (number of nodes) -
        1, unless a mapping between nodes and indeces is provided. graph can be,
        for example, a networkx.DiGraph.
    m: dict (optional)
        A map between nodes in the graph graph and their indeces.
    count_disconnected: bool (optional)
        Determines whether the unconnected triads should be counted as well.
    record_triads: bool (optional)
        Determines whether node-triples making up one triad should be recorded
        in a separate dictionary.

    Returns
    -------
    dict:
        Dictionary with triad names as keys and number of occurances as values.
    dict (optional):
        Dictionary with triad names as keys and lists with node triples as
        values.

    Refrences
    ---------
    .. [1] A subquadratic triad census algorithm for large sparse networks with
        small maximum degree. Vladimir Batagelj and Andrej Mrvar, University of
        Ljubljana. http://vlado.fmf.uni-lj.si/pub/networks/doc/triads/triads.pdf
    """

    def _tricode(graph, v, u, w):
        """
        This is some fancy magic that comes from Batagelj and Mrvar's paper.
        It treats each link between nodes v, u, w as a bit in the binary
        representation of an integer. This number is then mapped to one of the 16
        triad types that it represents.
        """
        combos = ((v, u, 1), (u, v, 2), (v, w, 4), (w, v, 8), (u, w, 16),
                (w, u, 32))
        return sum(x for (u, v, x) in combos if v in graph[u])

    def _count_connected():
        for v in graph:
            nbrs = set(graph.pred[v])
            nbrs.update(graph.succ[v])
            for u in nbrs:
                if u <= v:
                    continue
                neighbors = nbrs.union(set(graph.pred[u]))
                neighbors.update(graph.succ[u])
                neighbors.remove(u)
                neighbors.remove(v)
                # count connected triads
                for w in neighbors:
                    if (u < w) or (v < w and\
                            w < u and\
                            not v in graph.pred[w] and\
                            not v in graph.succ[w]):
                        code = _tricode(graph, v, u, w)
                        census[tricode_to_name[code]] += 1
                        if record_triads:
                            record[tricode_to_name[code]].append((v, u, w))

    def _count_mapped_connected():
        for v in graph:
            nbrs = set(graph.pred[v])
            nbrs.update(graph.succ[v])
            for u in nbrs:
                if m[u] <= m[v]:
                    continue
                neighbors = nbrs.union(set(graph.pred[u]))
                neighbors.update(graph.succ[u])
                neighbors.remove(u)
                neighbors.remove(v)
                # count connected triads
                for w in neighbors:
                    if (m[u] < m[w]) or (m[v] < m[w] and\
                            m[w] < m[u] and\
                            not v in graph.pred[w] and\
                            not v in graph.succ[w]):
                        code = _tricode(graph, v, u, w)
                        census[tricode_to_name[code]] += 1
                        if record_triads:
                            record[tricode_to_name[code]].append((v, u, w))

    def _count_disconnected():
        for v in graph:
            nbrs = set(graph.pred[v])
            nbrs.update(graph.succ[v])
            for u in nbrs:
                if u <= v:
                    continue
                neighbors = nbrs.union(set(graph.pred[u]))
                neighbors.update(graph.succ[u])
                neighbors.remove(u)
                neighbors.remove(v)
                # calculate dyadic triads instead of counting them
                if v in graph[u] and u in graph[v]:
                    census["102"] += n - len(neighbors) - 2
                else:
                    census["012"] += n - len(neighbors) - 2
                # count connected triads
                for w in neighbors:
                    if (u < w) or (v < w and\
                            w < u and\
                            not v in graph.pred[w] and\
                            not v in graph.succ[w]):
                        code = _tricode(graph, v, u, w)
                        census[tricode_to_name[code]] += 1
                        if record_triads:
                            record[tricode_to_name[code]].append((v, u, w))

    def _count_mapped_disconnected():
        for v in graph:
            nbrs = set(graph.pred[v])
            nbrs.update(graph.succ[v])
            for u in nbrs:
                if m[u] <= m[v]:
                    continue
                neighbors = nbrs.union(set(graph.pred[u]))
                neighbors.update(graph.succ[u])
                neighbors.remove(u)
                neighbors.remove(v)
                # calculate dyadic triads instead of counting them
                if v in graph[u] and u in graph[v]:
                    census["102"] += n - len(neighbors) - 2
                else:
                    census["012"] += n - len(neighbors) - 2
                # count connected triads
                for w in neighbors:
                    if (m[u] < m[w]) or (m[v] < m[w] and\
                            m[w] < m[u] and\
                            not v in graph.pred[w] and\
                            not v in graph.succ[w]):
                        code = _tricode(graph, v, u, w)
                        census[tricode_to_name[code]] += 1
                        if record_triads:
                            record[tricode_to_name[code]].append((v, u, w))

    if not graph.is_directed():
        raise nx.NetworkXError("not defined for undirected graphs")

    # initialze the census to zero
    census = dict((n, 0) for n in triad_names)
    if record_triads:
        record = dict((n, list()) for n in triad_names)
    n = graph.order()
    if count_disconnected:
        if m:
            count = _count_mapped_disconnected
        else:
            count = _count_disconnected
    else:
        if m:
            count = _count_mapped_connected
        else:
            count = _count_connected
        census.pop("003")
        census.pop("012")
        census.pop("102")
        if record_triads:
            record.pop("003")
            record.pop("012")
            record.pop("102")

    count()

    if count_disconnected:
        # null triads = total number of possible triads - all found triads
        census["003"] = ((n * (n - 1) * (n - 2)) / 6) - sum(census.itervalues())
    if record_triads:
        return (census, record)
    else:
        return census

################################################################################

if __name__ == "__main__":
    import timeit
    G = nx.read_edgelist("random_graph.edgelist", create_using=nx.DiGraph(),
            nodetype=int)
    mapping = dict(itertools.izip(G.nodes_iter(), itertools.count()))
    t2 = timeit.Timer(stmt="triadic_census(G)",
            setup="from __main__ import triadic_census;from __main__ import G")
    t3 = timeit.Timer(stmt="triadic_census(G, count_disconnected=True)",
            setup="from __main__ import triadic_census;from __main__ import G")
    t4 = timeit.Timer(stmt="triadic_census(G, m=mapping)",
            setup="from __main__ import triadic_census;from __main__ import G;"\
            "from __main__ import mapping")
    t5 = timeit.Timer(stmt="triadic_census(G, m=mapping, count_disconnected=True)",
            setup="from __main__ import triadic_census;from __main__ import G;"\
            "from __main__ import mapping")
    times2 = t2.repeat(repeat=30, number=5)
    times3 = t3.repeat(repeat=30, number=5)
    times4 = t4.repeat(repeat=30, number=5)
    times5 = t5.repeat(repeat=30, number=5)
    print "default census time mean", numpy.mean(times2), "+/-", numpy.std(times2)
    print "with disconnected census time mean", numpy.mean(times3), "+/-", numpy.std(times3)
    print "using mapping census time mean", numpy.mean(times4), "+/-", numpy.std(times4)
    print "with disconnected using mapping census time mean", numpy.mean(times5), "+/-", numpy.std(times5)

