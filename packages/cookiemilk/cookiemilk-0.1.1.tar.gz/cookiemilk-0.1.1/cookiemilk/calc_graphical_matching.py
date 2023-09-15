#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .numerical_sim import *
import networkx as nx


def calc_graphical_matching(
        graph1,
        graph2
):

    links_num1 = nx.diameter(graph1)
    links_num2 = nx.diameter(graph2)
    s = numerical_sim(links_num1, links_num2)

    return float('%.4f' % s)
