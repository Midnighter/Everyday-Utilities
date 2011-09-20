#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
==================
Network Algorithms
==================

:Author:
    Moritz Emanuel Beber
:Date:
    2011-03-07
:Copyright:
    Copyright(c) 2011 Jacobs University of Bremen. All rights reserved.
:File:
    algorithms.py
"""


import itertools
import numpy
import networkx as nx

from Queue import Queue


def graph_symmetries(graph):
    """
    Finds all symmetries of a graph. This is computationally very expensive
    O(N!) where N is the number of nodes in graph.
    """
    permutations = [dict(zip(graph.nodes_iter(), perm)) for perm in
            itertools.permutations(graph.nodes_iter())]
    keys = subgraph.nodes()
    keys.sort()
    symmetries = [[perm[node] for node in keys] for perm in permutations if
            all(graph.has_edge(perm[src], perm[tar])
            for (src, tar) in graph.edges_iter())]
    return symmetries

def kernighan_lin_refinement(s, b):
    """
    Parameters
    ----------
    s: array-like
        State vector partitioning the nodes into communities (contains 1s and
        -1s).
    b: matrix
        Modularity matrix.
    """
    dot = numpy.dot

    def flip(v, pos):
        v[pos] = -v[pos]
        dq = dot(v, dot(b.A, v))
        v[pos] = -v[pos]
        return dq

    s_len = len(s)
    trials = numpy.zeros(s_len)
    q_max = dot(s, dot(b.A, s))
    while True:
        for i in xrange(s_len):
            trials[i] = flip(s, i)
        dq = trials.max()
        if dq > q_max:
            i = trials.argmax()
            s[i] = -s[i]
            q_max = dq
        else:
            break

def spectral_community_detection(graph, weighted=True, threshold=1E-12,
        error_margin=1E-12, refine=True, max_iter=500):
    """
    Finds communities in a graph via spectral partitioning.

    Requires a graph whose nodes are integers from 0 to (number of nodes - 1).
    """
    dot = numpy.dot
    norm = numpy.linalg.norm
    ix = numpy.ix_
    kronecker = numpy.kron
    array = numpy.array
    real = numpy.real
    eigensystem = numpy.linalg.eig

    def _split(nbunch):
        len_nodes = len(nbunch)
        # use the relevant subpart of the modularity matrix
        sub_b = b[ix(nbunch, nbunch)].copy()
        # copy because we now modify elements
        for i in range(len_nodes):
            sub_b[i, i] -= sub_b[i, :].sum()
        # eigenvalues, eigenvectors
        (w, v) = eigensystem(sub_b)
        # find largest positive eigenvalue
        i = real(w).argmax()
        # convert to sign vector as defined on pg. 8579
        s = array([(1 if x > 0 else -1) for x in real(v[:, i])])
#        # find the dominant eigenvector by power method as in eq. 7
#        vec_new = numpy.ones(len_nodes)
##        vec_new = numpy.random.random_sample(len_nodes)
##        vec_new /= norm(vec_new)
#        for i in range(max_iter):
#            vec_old = vec_new
##            vec_new = dot(sub_adj.A, vec_old) - (dot(deg, dot(deg, vec_old)) / m2)
#            vec_new = dot(sub_b.A, vec_old)
#            vec_new /= norm(vec_new)
##            if abs(vec_new - vec_old).sum() < threshold:
#            if (norm(vec_new - vec_old) / norm(vec_old)) < threshold:
#                break
#        if i == max_iter:
#            raise UtilsError("power method failed to converge")
#        # convert to sign vector as defined on pg. 8579
#        s = array([(1 if x > 0 else -1) for x in vec_new])
        # dQ as in eq. 2 and 5
        d_q = dot(s, dot(sub_b.A, s)) / m4
        if d_q <= error_margin:
            return False
        if refine:
            kernighan_lin_refinement(s, sub_b)
            d_q = dot(s, dot(sub_b.A, s)) / m4
        spectral_community_detection.modularity += d_q
        group1 = list()
        group2 = list()
        for (i, sign) in enumerate(s):
            if sign > 0:
                group1.append(nbunch[i])
            else:
                group2.append(nbunch[i])
        return [group1, group2]

    if graph.is_directed():
        raise nx.NetworkXError("only undirected graphs are allowed")
    # basic measures
    n = graph.order()
    m2 = graph.size() * 2.0
    m4 = m2 * 2.0
    if n == 0 or m2 == 0:
        raise nx.NetworkXError("graph does not contain any nodes or links")
    nbunch = sorted(graph.nodes())
    indices = range(n)
    mapping = dict(itertools.izip(indices, nbunch))
    # construct adjacency matrix
    if nx.density(graph) < 0.5:
        adj = nx.to_scipy_sparse_matrix(graph, nodelist=nbunch)
    else:
        adj = nx.to_numpy_matrix(graph, nodelist=nbunch)
    # store the degree of each node in an array at corresponding index
    degrees = adj.sum(axis=0).A1
    # construct modularity matrix
    b = adj - (kronecker(degrees, degrees) / m2).reshape(n, n)
    # initialize algorithm
    communities = list()
    spectral_community_detection.modularity = 0.0
    partitions = Queue()
    partitions.put(indices)
    while not partitions.empty():
        indices = partitions.get()
        if not indices:
            continue
        groups = _split(indices)
        if not groups:
            communities.append(set([mapping[i] for i in indices]))
        else:
            partitions.put(groups[0])
            partitions.put(groups[1])
    return (spectral_community_detection.modularity, communities)

def directed_spectral_community_detection(graph, weighted=True, threshold=1E-12,
        refine=True):
    """
    """
    dot = numpy.dot
    ix = numpy.ix_
    kronecker = numpy.kron
    array = numpy.array
    real = numpy.real
    eigensystem = numpy.linalg.eig

    def _split(nbunch):
        len_nodes = len(nbunch)
        # use the relevant subpart of the modularity matrix
        sub_b = b[ix(nbunch, nbunch)].copy()
        # copy because we now modify elements
        for i in range(len_nodes):
            sub_b[i, i] -= (sub_b[i, :].sum() + sub_b[:, i].sum()) / 2.0
        # eigenvalues, eigenvectors
        (w, v) = eigensystem(sub_b)
        # find largest positive eigenvalue
        i = real(w).argmax()
        # convert to sign vector as defined on pg. 8579
        s = array([(1 if x > 0 else -1) for x in real(v[:, i])])
        # dQ as in eq. 2 and 5
        d_q = dot(s, dot(sub_b.A, s)) / m4
        if d_q <= threshold:
            return False
        if refine:
            kernighan_lin_refinement(s, sub_b)
            d_q = dot(s, dot(sub_b.A, s)) / m4
        spectral_community_detection.modularity += d_q
        group1 = list()
        group2 = list()
        for (i, sign) in enumerate(s):
            if sign > 0:
                group1.append(nbunch[i])
            else:
                group2.append(nbunch[i])
        return (group1, group2)

    if not graph.is_directed():
        raise nx.NetworkXError("only directed graphs are allowed")
    # basic measures
    n = graph.order()
    m = float(graph.size())
    m4 = m * 4.0
    if n == 0 or m == 0:
        raise nx.NetworkXError("graph does not contain any nodes or links")
    nbunch = sorted(graph.nodes())
    indices = range(n)
    mapping = dict(itertools.izip(indices, nbunch))
    # construct adjacency matrix
    if nx.density(graph) < 0.5:
        adj = nx.to_scipy_sparse_matrix(graph, nodelist=nbunch)
    else:
        adj = nx.to_numpy_matrix(graph, nodelist=nbunch)
    # networkx adjacency matrix Aij = 1 if there is a link i -> j
    # the paper uses the other orientation
    adj = adj.T
    # store the degree of each node in an array at corresponding index
    in_degrees = adj.sum(axis=0).A1
    out_degrees = adj.sum(axis=1).A1
    # construct modularity matrix
    b = adj - (kronecker(in_degrees, out_degrees) / m).reshape(n, n)
    # symmetrize
    b = b + b.T
    # initialize algorithm
    communities = list()
    spectral_community_detection.modularity = 0.0
    partitions = Queue()
    partitions.put(indices)
    while not partitions.empty():
        indices = partitions.get()
        if not indices:
            continue
        groups = _split(indices)
        if not groups:
            communities.append(set([mapping[i] for i in indices]))
        else:
            partitions.put(groups[0])
            partitions.put(groups[1])
    return (spectral_community_detection.modularity, communities)

