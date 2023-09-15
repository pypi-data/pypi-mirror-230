#!/usr/bin/env python
# -*- coding: utf-8 -*-

def numerical_sim(
        value1,
        value2
):

    s = 1 - abs(value1 - value2)/max(value1, value2)

    return float('%.4f' % s)
