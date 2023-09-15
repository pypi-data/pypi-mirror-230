#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import networkx as nx


def calc_gcent(
        G
):
    # Get data
    array = nx.to_numpy_array(G)
    n = G.number_of_nodes()
    node_degree = np.sum(array, axis=0)

    # Calculation
    ncent = node_degree/(n - 1)
    max_ncent = np.max(ncent)
    gcent = np.sum((max_ncent - ncent)/(n - 2))

    return float('%.4f' % gcent)
