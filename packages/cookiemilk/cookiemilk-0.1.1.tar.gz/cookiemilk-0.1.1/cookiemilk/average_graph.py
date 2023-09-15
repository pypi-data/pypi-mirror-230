#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .cmap2graph import *
import networkx as nx
from heapq import nlargest


def average_graph(
        data,
        key_terms,
        pfnet=True,
        max=1,
        min=0.1,
        r=np.inf,
        n_core=None,
        detailed=True
):

    # Step 1: obtain matrix data. For each graph, convert data into an n*n similarity matrix (n = number of the given
    # "key_terms") with 1 = 'connected' and 0 = 'unconnected', and then save in 'all_m'
    all_m = []
    for x in range(0, len(data)):
        m = [[0 for i in range(len(key_terms))] for j in range(len(key_terms))]  # an n*n zero matrix

        for pair in data[x].edges:  # add edges
            i = key_terms.index(pair[0])
            j = key_terms.index(pair[1])
            m[i][j] = 1
            m[j][i] = 1

        all_m.append(m)

    # Step 2: generate an average matrix
    average_m = np.array([[0 for i in range(len(key_terms))] for j in range(len(key_terms))])  # an n*n zero matrix
    for i in range(0, len(all_m)):
        average_m = average_m + np.array(all_m[i])
    average_m = average_m/len(all_m)

    # Step 3: define a NetworkX graph and calculate the corresponding PFNet if pfnet=True
    if not pfnet:
        average_ks = nx.Graph()
        average_ks.add_nodes_from(key_terms)
        pairs = []
        for i in range(0, len(average_m)):
            for j in range(0, len(average_m)):
                if i != j:
                    pairs.append([key_terms[i], key_terms[j], average_m[i, j]])
        average_ks.add_weighted_edges_from(pairs)
    else:
        average_ks = cmap2graph(data=average_m, data_type='array', key_terms=key_terms, read_from_file=False,
                                pfnet=True, max=max, min=min, r=r)

    # Step 4: remove non-core terms and related links if n_core is not None
    if n_core:
        degree = dict(nx.degree_centrality(average_ks))
        core = nlargest(n_core, degree, key=degree.get)

        for pair in list(average_ks.edges):  # remove links
            if pair[0] not in core or pair[1] not in core:
                average_ks.remove_edge(pair[0], pair[1])
        for term in key_terms:
            if term not in core:
                if term in average_ks.nodes:
                    average_ks.remove_node(term)

    if detailed:
        print('An average graph containing {} terms is generated successfully'.format(len(average_ks.nodes)))

    return average_ks
