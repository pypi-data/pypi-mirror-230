#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .numerical_sim import *


def calc_surface_matching(
        graph1,
        graph2
):

    links_num1 = graph1.number_of_edges()
    links_num2 = graph2.number_of_edges()
    s = numerical_sim(links_num1, links_num2)

    return float('%.4f' % s)
