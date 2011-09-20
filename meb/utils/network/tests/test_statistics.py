#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
===========================
Modularity of Real Networks
===========================

:Author:
    Moritz Emanuel Beber
:Date:
    2011-03-17
:Copyright:
    Copyright(c) 2011 Jacobs University of Bremen. All rights reserved.
:File:
    test_statistics.py
"""


import tarfile
import os
import networkx as nx
import pajek_patch as pp
import meb.utils.network.statistics as net_stat
from community import detect_communities


def test_modularity_measure(function):

    def print_info(graph, name):
        print name, "N:", len(graph), "M:", graph.size()
        print "Q:", round(function(graph)[0], 3)

    graph = nx.read_gml(archive.extractfile("networks/karate-newman-1977.gml"))
    print_info(graph, "Karate")
    graph = nx.read_gml(archive.extractfile("networks/yeast_protein_interaction-barabasi-2001.tsv"))
    print_info(graph, "Protein Interaction")
    graph = pp.read_pajek(zipfile.ZipFile("networks/jazz.zip",
        "r").open("jazz.net"))
    print_info(graph, "Jazz musicians")
    graph = pp.read_pajek(zipfile.ZipFile("networks/celegans_metabolic.zip",
        "r").open("celegans_metabolic.net"))
    print_info(graph, "Metabolic")
    graph = nx.read_edgelist(zipfile.ZipFile("networks/email.zip",
        "r").open("email.txt"), data=False)
    print_info(graph, "E-mail")
    graph = pp.read_pajek(zipfile.ZipFile("networks/PGP.zip",
        "r").open("PGPgiantcompo.net"))
    print_info(graph, "Key signing")
    graph = nx.read_gml(zipfile.ZipFile("networks/cond-mat-2003.zip",
        "r").open("cond-mat-2003.gml"))
    print_info(graph, "Physicists")

def test_degree_correlation_measure(archive, function):

    def print_info(graph, name):
        print name, "N:", len(graph), "M:", graph.size()
        print "r:", round(function(graph), 3)

#    graph = nx.read_gml(archive.extractfile("networks/cond_mat-newman-1999.gml"))
#    print_info(graph, "Physicists")
#    graph = nx.read_adjlist(archive.extractfile("networks/actor-barabasi-1999.adj"))
#    print_info(graph, "Actors")
#    graph = nx.read_edgelist(archive.extractfile("networks/www-barabasi-1999.tsv"),
#            data=False)
#    print_info(graph, "WWW")
    graph = nx.read_edgelist(archive.extractfile("networks/yeast_protein_interaction-barabasi-2001.tsv"),
            data=False)
    print_info(graph, "Protein Interaction")


if __name__ == "__main__":
    archive = tarfile.open("real_world_networks.tar.bz2", mode="r:bz2")
    test_degree_correlation_measure(archive, net_stat.degree_correlation_coefficient)
