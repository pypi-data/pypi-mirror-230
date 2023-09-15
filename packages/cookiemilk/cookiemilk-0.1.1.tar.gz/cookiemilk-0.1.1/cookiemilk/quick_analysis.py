#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .average_graph import *
from .calc_gcent import *
from .calc_graphical_matching import *
from .calc_surface_matching import *
from .calc_tversky import *
from .cmap2graph import *
from .draw import *
from .numerical_sim import *
from .pathfinder_network import *
from .text2graph import *

import csv
from datetime import datetime
import networkx as nx
import numpy as np
import os


def quick_analysis(
        folder,
        data_type,
        key_terms=None,
        synonym=None,
        as_lower=None,
        pfnet=False,
        max=None,
        min=None,
        r=np.inf,
        encoding=None,
        read_from=None,

        referent_type=None,
        r_key_terms=None,
        r_synonym=None,
        r_as_lower=None,
        r_pfnet=False,
        r_max=None,
        r_min=None,
        r_r=np.inf,
        r_encoding=None,
        r_read_from=None,

        calculation=None,
        alpha=0.5,

        save_figures=True,
        save_average_figures=False,
        n_core=None,

        canvas_size=(500, 500),
        node_font='sans-serif',
        node_fontsize=12,
        node_fontcolour='black',
        node_fillcolour='lightgrey',
        node_size=12,
        edge_colour='lightgrey',
        edge_size=2,
        edge_distance=100,
        charge=-300,
        window_size=(600, 600)
):
    # Error messages
    for calc in calculation:
        if calc not in ['density', 'GC', 's_density', 's_GC', 's_surface',
                        's_graphical', 's_concept', 's_link', 's_semantic']:
            raise ValueError(f'The indicator "{calc}" in "calculation" is unrecognized.')

    # Step 1: define a dictionary object to store data
    data = dict()

    # Step 2: obtain filenames of data
    file_path = []
    for root, dirs, files in os.walk(folder):
        for file in files:
            file_path.append(os.path.join(root, file))

    # Step 3: convert data to graph
    # data
    my_graph = []
    my_id = []
    my_file = []
    for file in file_path:
        if '/data' in file and '.DS_Store' not in file:  # fuck Apple

            print('Constructing: ', file)

            my_id.append(file[-8:-4])
            my_file.append(file)

            if data_type in ['proposition', 'array']:
                my_graph.append(cmap2graph(data=file, data_type=data_type, key_terms=key_terms,
                                           read_from_file=True, read_from=read_from, encoding=encoding,
                                           pfnet=pfnet, max=max, min=min, r=r))
            elif data_type == 'text':
                my_graph.append(text2graph(data=file, key_terms=key_terms, synonym=synonym,
                                           as_lower=as_lower, read_from_file=True, encoding=encoding,
                                           pfnet=pfnet, max=max, min=min, r=r))

    # referent
    ref = None
    ref_file = None
    for file in file_path:
        if '/ref.' in file and '.DS_Store' not in file:  # fuck Apple

            ref_file = file

            if referent_type in ['proposition', 'array']:
                ref = cmap2graph(data=file, data_type=referent_type, key_terms=r_key_terms,
                                 read_from_file=True, read_from=r_read_from, encoding=r_encoding,
                                 pfnet=r_pfnet, max=r_max, min=r_min, r=r_r)
            elif referent_type == 'text':
                ref = text2graph(data=file, key_terms=r_key_terms, synonym=r_synonym,
                                 as_lower=r_as_lower, read_from_file=True, encoding=r_encoding,
                                 pfnet=r_pfnet, max=r_max, min=r_min, r=r_r)

            break

    # Step 4: calculation
    data['id'] = my_id
    data['filepath'] = my_file
    data.update({"ref_filepath": [ref_file for graph in my_graph]})

    data.update({"n_concept": [len(graph.nodes) for graph in my_graph]})
    data.update({"n_link": [len(graph.edges) for graph in my_graph]})
    data.update({"ref_n_concept": [len(ref.nodes) for graph in my_graph]})
    data.update({"ref_n_link": [len(ref.edges) for graph in my_graph]})

    if 'density' in calculation:
        data.update({"density": [float('%.4f' % nx.density(graph)) for graph in my_graph]})
        data.update({"ref_density": [float('%.4f' % nx.density(ref)) for graph in my_graph]})

    if 'GC' in calculation:
        data.update({"GC": [calc_gcent(graph) for graph in my_graph]})
        data.update({"ref_GC": [calc_gcent(ref) for graph in my_graph]})

    if 's_surface' in calculation:
        data.update({"s_surface": [calc_surface_matching(graph, ref) for graph in my_graph]})

    if 's_graphical' in calculation:
        data.update({"s_graphical": [calc_graphical_matching(graph, ref) for graph in my_graph]})

    if 's_density' in calculation:
        data.update({'s_density': [numerical_sim(nx.density(graph), nx.density(ref)) for graph in my_graph]})

    if 's_GC' in calculation:
        data.update({'s_GC': [numerical_sim(calc_gcent(graph), calc_gcent(ref)) for graph in my_graph]})

    if 's_concept' in calculation:
        data.update(
            {"s_concept": [calc_tversky(graph, ref, comparison='conceptual', alpha=alpha) for graph in my_graph]})

    if 's_link' in calculation:
        data.update(
            {"s_link": [calc_tversky(graph, ref, comparison='propositional', alpha=alpha) for graph in my_graph]})

    if 's_semantic' in calculation:
        data.update(
            {"s_semantic": [calc_tversky(graph, ref, comparison='semantic', alpha=alpha) for graph in my_graph]})

    # Step 6: save the output file
    if folder:
        now = datetime.now()
        otuput_name = folder + '/quick_analysis_' + now.strftime("%Y%m%d_%H%M%S") + '.csv'

        csv_file = open(otuput_name, 'w', encoding=encoding, newline='')
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(data.keys())
        for row in zip(*data.values()):
            csv_writer.writerow(row)
        csv_file.close()

    # Step 7: visualization
    if save_figures:

        subfolder = os.path.join(folder, 'networks/')
        if not os.path.exists(subfolder):
            os.makedirs(subfolder)

        for i in range(0, len(my_graph)):
            draw(my_graph[i], show=False, save=True, filename=subfolder + data['id'][i], encoding=encoding,
                 canvas_size=canvas_size, node_font=node_font, node_fontsize=node_fontsize,
                 node_fontcolour=node_fontcolour, node_fillcolour=node_fillcolour, node_size=node_size,
                 edge_colour=edge_colour, edge_size=edge_size, edge_distance=edge_distance, charge=charge,
                 window_size=window_size, detailed=False)

        draw(ref, show=False, save=True, filename=subfolder + 'ref', encoding=encoding,
             canvas_size=canvas_size, node_font=node_font, node_fontsize=node_fontsize,
             node_fontcolour=node_fontcolour, node_fillcolour=node_fillcolour, node_size=node_size,
             edge_colour=edge_colour, edge_size=edge_size, edge_distance=edge_distance, charge=charge,
             window_size=window_size, detailed=False)

    # # Step 8: average networks
    if save_average_figures:

        subfolder = os.path.join(folder, 'networks/')
        if not os.path.exists(subfolder):
            os.makedirs(subfolder)

        my_average = average_graph(my_graph, key_terms=key_terms, pfnet=True, max=1, min=0.1, r=np.inf,
                                   n_core=n_core, detailed=False)

        draw(my_average, show=False, save=True, filename=subfolder + 'average', encoding=encoding,
             canvas_size=canvas_size, node_font=node_font, node_fontsize=node_fontsize,
             node_fontcolour=node_fontcolour, node_fillcolour=node_fillcolour, node_size=node_size,
             edge_colour=edge_colour, edge_size=edge_size, edge_distance=edge_distance, charge=charge,
             window_size=window_size, detailed=False)

    # Message
    print('Done.')
    return data
