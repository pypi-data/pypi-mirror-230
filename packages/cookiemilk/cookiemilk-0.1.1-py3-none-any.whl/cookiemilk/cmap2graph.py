# !/usr/bin/env python
# -*- coding: utf-8 -*-

import networkx as nx
from os.path import basename
from .pathfinder_network import *


def cmap2graph(
        data,
        data_type,
        key_terms=None,
        read_from_file=True,
        read_from=0,
        encoding='utf-8',
        pfnet=False,
        max=None,
        min=None,
        r=np.inf
):
    # Error messages
    if data_type not in ['proposition', 'array']:
        raise ValueError('The value of "data_type" is unrecognized, it must be either "pair" or "array"!')

    if key_terms is not None:
        if not isinstance(key_terms, list):
            raise TypeError('The "key_terms" must be a list object.')
        if not key_terms:
            raise ValueError('The "key_terms" is an empty list.')

    # Step 1: define a graph
    G = nx.Graph()

    # Step 2: read the file content if read_from_file=True
    if read_from_file:
        f = open(data, 'r', encoding=encoding)
        content = [line.strip('\n').split('\t') if '\t' in line
                   else line.strip('\n').split() for line in f]
        G.name = basename(data.split('.')[0])
    else:
        content = list(data)

    # Step 3: Skip the unwanted content based on the argument "read_from"
    if type(read_from) == int:
        content = content[read_from:]

    # Step 4: conduct the following processing when data_type="proposition"
    if data_type == 'proposition':
        # Step 4-1: add edges
        for pair in content:
            G.add_edge(pair[0], pair[1])
        # Step 4-2: calculate the PFNet if pfnet=True
        if pfnet:
            G = pathfinder_network(G, max=max, min=min, r=r)

    # Step 5: conduct the following processing when data_type="array"
    elif data_type == 'array':
        # Step 5.1: convert the data into a full matrix if it is a triangle matrix
        if len(content[0]) != len(content[-1]):
            content.insert(0, ['0'])
            for i in range(0, len(content)):
                while len(content[i]) != len(content):
                    content[i].append('')
            for i in range(len(content)):
                for j in range(i + 1, len(content)):
                    content[j][i] = content[i][j]

        # Step 5-2: convert each value from string to integer and then add values into a new array
        array = np.zeros([len(content), len(content)])
        for i in range(0, len(content)):
            for j in range(0, len(content)):
                array[i, j] = float(content[i][j])

        # Step 5-3: calculate the PFNet if pfnet=True
        if pfnet:
            if max is not None and min is not None:
                array = max - array + min
                array = np.where((array >= min) & (array <= max), array, np.inf)
            array = floyd(array, r=r)
            np.fill_diagonal(array, False)

        # Step 5-4: add edges
        pairs = []
        if pfnet:
            start, end = np.where(np.tril(array) == True)
            for i in range(0, len(start)):
                pairs.append([key_terms[start[i]], key_terms[end[i]]])
            G.add_edges_from(pairs)
        else:
            for i in range(0, len(key_terms)):
                for j in range(0, len(key_terms)):
                    if array[i, j] != 0 and i != j:
                        pairs.append([key_terms[i], key_terms[j], array[i, j]])
            G.add_weighted_edges_from(pairs)

    return G
