#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
================
Network Rewiring
================

:Author:
    Moritz Emanuel Beber
:Date:
    2011-03-01
:Copyright:
    Copyright(c) 2011 Jacobs University of Bremen. All rights reserved.
:File:
    randomisation.py
"""


import numpy
import networkx as nx


def standard_directed_groups(graph):
    """
    Makes two categories of unidirectional and bidirectional links.

    Note
    ----
    Self-links are recognised as bidirectional links and produce an error.
    """
    if graph.number_of_selfloops() > 0:
        raise nx.NetworkXError("the standard setup does not allow self-links")
    uni = list()
    bi = list()
    for edge in graph.edges_iter():
        if graph.has_edge(edge[1], edge[0]):
            bi.append(edge)
        else:
            uni.append(edge)
    return [[uni, 1], [bi, 2]]

def metabolic_directed_groups(graph):
    """
    Separates reversible and irreversible reactions and for each of them groups
    links in substrate-reaction and reaction-product pairs.
    """
    prod_forward = list()
    subs_forward = list()
    prod_reversible = list()
    subs_reversible = list()
    for rxn in graph.reactions:
        if rxn.reversible:
            prod_group = prod_reversible
            subs_group = subs_reversible
        else:
            prod_group = prod_forward
            subs_group = subs_forward
        for cmpd in graph.predecessors_iter(rxn):
            subs_group.append((cmpd, rxn))
        for cmpd in graph.successors_iter(rxn):
            prod_group.append((rxn, cmpd))
    return [[prod_forward, 1], [subs_forward, 1], [prod_reversible, 1],
            [subs_reversible, 1]]

def selflinks_directed_groups(graph):
    """
    Normal categorisation of links with the addition of self-links as
    unidirectional links.
    """
    uni = list()
    bi = list()
    for edge in graph.edges_iter():
        if edge[0] == edge[1]:
            uni.append(edge)
        elif graph.has_edge(edge[1], edge[0]):
            bi.append(edge)
        else:
            uni.append(edge)
    return [[uni, 1], [bi, 2]]

def check_standard(graph, first, second):
    """
    Standard rewiring conditions as in original theory.
    """
    # curiously the conditions for switching unidirectional and bidirectional
    # links are the same for just slightly different reasons
    if first == second:
        return False
    # prevent creation of self-links
    if first[0] == second[1]:
        return False
    if second[0] == first[1]:
        return False
    # check if we would create a parallel edge
    if second[1] in graph[first[0]]:
        return False
    if first[1] in graph[second[0]]:
        return False
    # check if we would create a bidirectional link
    # or cover existing reverse link in double link switching
    if first[0] in graph[second[1]]:
        return False
    if second[0] in graph[first[1]]:
        return False
    return True


class NetworkRewiring(object):
    """
    """

    def __init__(self):
        """
        """
        object.__init__(self)
        self.conditions = check_standard
        self.make_groups = standard_directed_groups
        self.graph = None

    def _add_edge(self, src, tar, bunch, i):
        """
        """
        self.graph.add_edge(src, tar)
        # over-write old edge
        bunch[i, 0] = src
        bunch[i, 1] = tar

    def _remove_edge(self, src, tar, bunch):
        """
        """
        self.graph.remove_edge(src, tar)

    def _switch_double(self, first, second, group, u, v):
        """
        """
        # find the reverse edges for u and v
        # indices of target(first)
        x = numpy.nonzero(group[:, 0] == first[1])[0]
        # intersection with indices of source(first) to find index
        x = x[numpy.nonzero(group[x, 1].flatten() == first[0])[0]]
        # similarly
        y = numpy.nonzero(group[:, 0] == second[1])[0]
        y = y[numpy.nonzero(group[y, 1].flatten() == second[0])[0]]
        if self.conditions(self.graph, first, second):
            # if all of these conditions are met, switch double edge
            # add the forward direction
            self._add_edge(first[0], second[1], group, u)
            self._add_edge(second[0], first[1], group, v)
            # add the backward direction
            self._add_edge(first[1], second[0], group, x)
            self._add_edge(second[1], first[0], group, y)
            # remove old edges
            self._remove_edge(first[0], first[1], group)
            self._remove_edge(first[1], first[0], group)
            self._remove_edge(second[0], second[1], group)
            self._remove_edge(second[1], second[0], group)
            return 1
        else:
            return 0

    def _switch_single(self, first, second, group, u, v):
        """
        """
        if self.conditions(self.graph, first, second):
            # all conditions passed
            self._add_edge(first[0], second[1], group, u)
            self._add_edge(second[0], first[1], group, v)
            self._remove_edge(first[0], first[1], group)
            self._remove_edge(second[0], second[1], group)
            return 1
        else:
            return 0

    def randomise(self, template, flip=100, copy=True):
        """
        This is achieved by switching edges in the graph a number of
        times equal to the number of edges present times 'flip'. This function
        is intended as a basis for calculating three-node subgraph statistics.
        As such only degrees of nodes, bi-directional link properties, etc. are
        conserved. For larger subgraph statistics also the smaller subgraph
        statistics would have to be conserved.

        Notes
        -----
        Nodes need to be integers.

        References
        ----------
        R Milo, S Shen-Orr, S Itzkovitz, N Kashtan, D Chklovskii & U Alon
        Network Motifs: Simple Building Blocks of Complex Networks
        Science, 298:824-827 (2002)
        """
        if template.is_multigraph():
            raise nx.NetworkXError("not defined for multigraphs")
        if copy:
            self.graph = template.copy()
        else:
            self.graph = template
        if not self.graph.size():
            return (self.graph, 0.0)
        sets = self.make_groups(self.graph)
        len_sets = len(sets)
        # set up progress tracking
        # the probability of switching a link in a certain group is proportional
        # to the number of flips left in that group
        # for each group we record:
        # expected flips, attempts left, successful flips
        track = numpy.zeros(shape=(len_sets, 4), dtype=int)
        for (i, (group, weight)) in enumerate(sets):
            w_group = len(group)
            # convert links groups to two dimensional array
            sets[i][0] = numpy.array(group)
            if w_group > weight:
                track[i, 0] = flip * weight * w_group # expected flips
                track[i, 1] = track[i, 0] # attempts left
                # store number of links - 1 for inclusive randint range
                track[i, 3] = w_group - 1
        total_left = track[:, 1].sum()
        try:
            probs = [float(track[k, 1]) / float(total_left)\
                    for k in xrange(len_sets)]
        except ZeroDivisionError:
            return (self.graph, 0.0)
        # randomly rewire groups depending on their probability
        uniform = numpy.random.random_sample
        randint = numpy.random.random_integers
        for i in xrange(total_left): # loop value is stored, so no problems
            draw = uniform()
            for j in xrange(len_sets):
                if draw < float(sum(probs[:j + 1])):
                    group = sets[j][0]
                    (u, v) = randint(0, track[j, 3], 2) # two random links
                    if sets[j][1] == 1:
                        track[j, 2] += self._switch_single(tuple(group[u]),
                                tuple(group[v]), group, u, v)
                    elif sets[j][1] == 2:
                        track[j, 2] += self._switch_double(tuple(group[u]),
                                tuple(group[v]), group, u, v)
                    else:
                        nx.NetworkXError("unknown category")
                    total_left -= 1
                    track[j, 1] -= 1
                    try:
                        probs = [float(track[k, 1]) / float(total_left)\
                                for k in xrange(len_sets)]
                    except ZeroDivisionError:
                        pass # end of randomisation
                    break # selected right category, continue with outer loop
        return (self.graph, float(track[:, 2].sum()) / float(track[:, 0].sum()))

