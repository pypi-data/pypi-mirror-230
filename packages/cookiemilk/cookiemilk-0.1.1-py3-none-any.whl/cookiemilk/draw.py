# !/usr/bin/env python
# -*- coding: utf-8 -*-

from webview import create_window, start


def draw(
        graph,
        show=True,
        save=False,
        filename='filename',
        encoding='utf-8',
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
        window_size=(600, 600),
        detailed=True
):

    # edges information
    edges = []
    for (u, v, wt) in graph.edges.data():
        # u and v are each node in a proposition
        edges.append({'source': f"{u}", 'target': f"{v}"})
    edges = f"{edges}"
    for i in ["source",
              "target"]:  # replace "'source'"/"'target'" to "source"/"target"
        edges = edges.replace(f"'{i}'", i)

    html = f"""
<!DOCTYPE html>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<style>

.link {{
    fill: {edge_colour};
    stroke: {edge_colour};
    stroke-width: {edge_size}px;
}}

.node circle {{
    fill: {node_fillcolour};
    stroke: {node_fillcolour};
    stroke-width: {node_size}px;
}}

text {{
    fill: {node_fontcolour};
    font: {node_fontsize}px {node_font};
    font-weight: bold;
    pointer-events: none;
}}

</style>
<body>
<script src="https://d3js.org/d3.v3.min.js"></script>
<script>
// this script derive from http://bl.ocks.org/mbostock/2706022

// http://blog.thomsonreuters.com/index.php/mobile-patent-suits-graphic-of-the-day/
const links = {edges};
const nodes = {{}};

// Compute the distinct nodes from the links.
links.forEach(function(link) {{
  link.source = nodes[link.source] || (nodes[link.source] = {{name: link.source}});
  link.target = nodes[link.target] || (nodes[link.target] = {{name: link.target}});
}});

const width = {canvas_size[0]},
        height = {canvas_size[1]};

const force = d3.layout.force()
        .nodes(d3.values(nodes))
        .links(links)
        .size([width, height])
        .linkDistance({edge_distance})
        .charge({charge})
        .on("tick", tick)
        .start();

const svg = d3.select("body").append("svg")
        .attr("width", width)
        .attr("height", height);

const link = svg.selectAll(".link")
        .data(force.links())
        .enter().append("line")
        .attr("class", "link");

const node = svg.selectAll(".node")
        .data(force.nodes())
        .enter().append("g")
        .attr("class", "node")
        .on("mouseover", mouseover)
        .on("mouseout", mouseout)
        .call(force.drag);

node.append("circle")
    .attr("r", 10);

node.append("text")
    .attr("dy", ".2em")
    .style("text-anchor", "middle")
    .text(function(d) {{ return d.name; }});

function tick() {{
  link
      .attr("x1", function(d) {{ return d.source.x; }})
      .attr("y1", function(d) {{ return d.source.y; }})
      .attr("x2", function(d) {{ return d.target.x; }})
      .attr("y2", function(d) {{ return d.target.y; }});

  node
      .attr("transform", function(d) {{ return "translate(" + d.x + "," + d.y + ")"; }});
}}

function mouseover() {{
  d3.select(this).select("circle").transition()
      .duration(750)
      .attr("r", 16);
}}

function mouseout() {{
  d3.select(this).select("circle").transition()
      .duration(750)
      .attr("r", 8);
}}

// d3.select("body").append("button")
//         .attr("type","button")
//         .attr("class", "downloadButton")
//         .text("Download SVG")
//         .on("click", function() {{
//             // download the svg
//             downloadSVG();
//         }});

</script>

    """

    if save:
        f = open(f'{filename}.html', 'a', encoding=encoding)
        f.write(html)
        f.close()
        if detailed:
            print(f'The visualized graph is saved as a file named "{filename}.html" successfully.')

    if graph.name:
        title = graph.name
    else:
        title = 'test'

    create_window(title=title,
                  html=html,
                  width=window_size[0],
                  height=window_size[1],
                  on_top=True)
    if show:
        start()
