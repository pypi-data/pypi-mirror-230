#!/usr/bin/env python
# -*- coding: utf-8 -*-

from re import finditer
import networkx as nx
from os.path import basename
from .pathfinder_network import *


def text2graph(
        data,
        key_terms,
        synonym=None,
        as_lower=True,
        read_from_file=True,
        encoding='utf-8',
        pfnet=False,
        max=None,
        min=None,
        r=np.inf
):
    # Error messages
    if key_terms is not None:
        if not isinstance(key_terms, list):
            raise TypeError('The "key_terms" must be a list object.')
        if not key_terms:
            raise ValueError('The "key_terms" is an empty list.')

    if synonym is not None:
        if not isinstance(synonym, dict):
            raise TypeError('The "synonym" must be a dictionary object.')
        if not synonym:
            raise ValueError('The "synonym" is an empty dictionary.')
        for key in synonym:
            if key not in key_terms:
                raise ValueError(f'The key "{key}" in "synonym" is not in "key_terms".')

    # Step 1: define a graph
    G = nx.Graph()

    # Step 2: read the file content if read_from_file=True
    if read_from_file:
        text = ''
        with open(data, "r", encoding=encoding) as f:
            for line in f:
                text += line.strip()
        data = text
        G.name = basename(data.split('.')[0])  # use the file name as the graph name

    # Step 3: convert the text into lowercase if as_lower=True
    if as_lower:
        data = data.lower()

    # Step 4: automatic correction of term order in "key_terms".
    # For example, when searching for "bees" in the text, it is necessary to check if this term is included in another
    # term, like "beeswax". If so, "bees" will be moved to the last position in "key_terms".
    while True:
        corrected = False
        for i, term in enumerate(key_terms):
            for j, other_term in enumerate(key_terms):
                if i < j and term in other_term:
                    key_terms.pop(i)
                    key_terms.append(term)
                    corrected = True
                    break
            if corrected:
                break
        if not corrected:
            break

    # Step 5: synonyms replacement if synonym=True
    if synonym is not None:
        for key_term in synonym.keys():
            for term in synonym[key_term]:
                data = data.replace(term, key_term)

    # Step 6: add every key term in the text to a word chain sequentially
    chain = []
    for term in key_terms:
        for index in finditer(term, data):
            if not chain or all(index.span()[0] < i[0][0] or index.span()[1] > i[0][1] for i in chain):
                chain.append([index.span(), key_terms.index(term)])
    chain.sort()  # sort by order of occurrence
    chain = list(x[1] for x in chain)  # keep index of terms only

    # Step 7: add edges and related nodes
    for i in range(0, len(chain) - 1):
        if chain[i] != chain[i + 1]:
            G.add_edge(key_terms[chain[i]], key_terms[chain[i + 1]])

    # Step 8: calculate the PFNet if pfnet=True
    if pfnet:
        G = pathfinder_network(G, max=max, min=min, r=r)

    return G
