
#
# Modification History:
#   180815 David Shifflett
#     added encoding option to the opening of MP code files
#

import os
from subprocess import Popen, PIPE
from PyQt5.QtCore import QPointF
import json
from node import Node
from edge import Edge
from graph_item import GraphItem
from settings_manager import settings
from path_constants import TRACE_GENERATED_OUTFILE

"""Manages open, save, import, and export operations.

Interfaces:

read_mp_code_file(mp_code_filename):
    read MP Code file.  Return (status, mp_code_text)

save_mp_code_file(self, mp_code_filename):
    save MP Code to file.  Return status

read_generated_json(generated_json):
    read generated JSON.  Return (status, graphs)

import_gry_file(gry_filename):
    import JGF Gryphon file.  Return (status, metadata fields and graphs)

NOTE: RIGAL functions read/write in same directory, so we change to the
scratch RIGAL work directory to work, then move back when done.
"""

# read MP Code file.  Return (status, mp_code_text)
def read_mp_code_file(mp_code_filename):
    try:
        # read file mp_code_filename into mp_code_text,
        # some Windows editors will add a 3 byte UTF-8 Byte Order Mark
        # (BOM) at the beginning of the file.
        # This doesn't cause a problem unless the first
        # thing in the file is an MP keyword, especially SCHEMA
        # open with the utf-8-sig encoding, removes the BOM
        with open(mp_code_filename, encoding='utf-8-sig') as f:
            mp_code_text = f.read()
        return ("", mp_code_text)

    except Exception as e:
        return ("Error reading MP Code file '%s': %s" % (mp_code_filename, str(e)), "")

# save MP Code to file.  Return status
def save_mp_code_file(mp_code_text, mp_code_filename):
    if not mp_code_filename:
        return "Error: save MP Code file filename not provided."

    try:
        # save lines with \n after each line
        with open(mp_code_filename, 'w') as f:
            f.write(mp_code_text)
        return ""
    except Exception as e:
        status = "Error sving file '%s': %s" % (mp_code_filename, str(e))
        return status

# read JSON that came from the trace generator.  Return (status, graphs)
# NOTE: per request, removes underscores from node label
def read_generated_json(generated_json_text):

    graphs = list()
    recommended_node_width = settings["node_width"]
    recommended_node_height = settings["node_height"]
    graph_h_spacing = settings["graph_h_spacing"]
    graph_v_spacing = settings["graph_v_spacing"]

    # parse generated_json_text
    try:
        generated_json = json.loads(generated_json_text)

        # write JSON from trace generator, indented with sorted keys
        with open(TRACE_GENERATED_OUTFILE, "w") as f:
            json.dump(generated_json, f, indent=4, sort_keys=True)

        # global view
        if "GLOBAL" in generated_json:
            print("Implementation TBD for GLOBAL:%s"%generated_json["GLOBAL"])

        i=1
        for trace in generated_json["traces"]:
            nodes = list()
            edges = list()

            # build graph from trace
            # item 0: graph mark, "U" or "M"
            graph_mark = trace[0]

            # item 1: trace probability
            trace_probability = trace[1]

            # item 2: event list of nodes
            node_lookup = dict() # helper for connecting edges
            json_nodes = trace[2]
            y_extra_say = 0
            for json_node in json_nodes:

                # prepare label without underscores
                label = json_node[0].replace('_'," ")

                # get x and y, not available in older JSON
                x=json_node[3] * graph_h_spacing + recommended_node_width/2
                y=json_node[4] * graph_v_spacing + recommended_node_height/2
                if json_node[1] == "T": # SAY
                    # spread out SAY boxes more
                    y_extra_say += 22 * (len(label)//20)
                    y += y_extra_say
#                    y=json_node[4]*1.8*graph_v_spacing+recommended_node_height

                # node_id, type, name, x, y, hide, collapse, collapse_below
                node = Node("%s"%json_node[2], json_node[1],
                              label, x, y, False, False, False)
                nodes.append(node)
                node_lookup[node.node_id] = node

            # item 3: IN relation edges
            json_edges = trace[3]
            for json_edge in json_edges:
                # source_id, relation, target_id, label
                edges.append(Edge("%s"%json_edge[1], "IN",
                                  "%s"%json_edge[0], "",
                                  node_lookup))

            # item 4: FOLLOWS relation edges
            json_edges = trace[4]
            for json_edge in json_edges:
                # source_id, relation, target_id, label
                edges.append(Edge("%s"%json_edge[1], "FOLLOWS",
                                  "%s"%json_edge[0], "",
                                  node_lookup))

            # items 5...n-1: the user-defined named relations
            for user_defined_json_edges in trace[5:]:
                if type(user_defined_json_edges) ==list:
                    label = user_defined_json_edges[0]
                    for json_edge in user_defined_json_edges[1:]:
                        # source_id, relation, target_id, label
                        edges.append(Edge("%s"%json_edge[0],
                                          "USER_DEFINED",
                                          "%s"%json_edge[1], label,
                                          node_lookup))
                elif type(user_defined_json_edges) ==dict:
                    # VIEWS
                    for key, value in user_defined_json_edges.items():
                        if value:
                            print("Implementation TBD for %s:%s"%(key, value))

            # build graph item from this
            graph_item = GraphItem(i, graph_mark, trace_probability,
                                                             nodes, edges)
            graphs.append(graph_item)

            i += 1

        return ("", graphs)

    except Exception as e:
        print("Error reading generated JSON text: %s" % (repr(e)))
        status = "No traces were generated."
        return (status, list())

# import JSON graph.  Return (status, metadata fields and graphs)
def import_gry_file(gry_filename):
    """Import JSON graph Gryphon file, return status, metadata fields
       and graphs."""

    # parse gry_filename
    try:
        # get json graph data
        json_data = json.load(open(gry_filename))

        # general attributes
        mp_code = json_data["mp_code"]
        scope = json_data["scope"]
        selected_index = json_data["selected_index"]
        scale = json_data["scale"]
        x_slider = json_data["x_slider"]
        y_slider = json_data["y_slider"]

        # graphs
        graphs = list()
        for json_graph in json_data["graphs"]:
            nodes = list()
            edges = list()

            # attributes
            index = json_graph["index"]
            graph_mark = json_graph["mark"]
            probability = json_graph["probability"]

            # nodes
            node_lookup = dict() # helper for connecting edges
            for n in json_graph["nodes"]:
                # node_id, type, name, x, y, hide, collapse, collapse_below
                node = Node(n["id"], n["type"], n["label"],
                            n["x"], n["y"], n["hide"],
                            n["collapse"], n["collapse_below"])
                nodes.append(node)
                node_lookup[node.node_id] = node

            # edges
            for e in json_graph["edges"]:
                cbp1 = QPointF(e["cbp1_x"], e["cbp1_y"])
                cbp2 = QPointF(e["cbp2_x"], e["cbp2_y"])
                # source_id, relation, target_id, label, cbp1, cbp2, node_lookup
                edge = Edge(e["source"], e["relation"], e["target"],
                            e["label"], node_lookup, cbp1, cbp2)
                edges.append(edge)

            # build graph item from this
            graph_item = GraphItem(index, graph_mark, probability, nodes, edges)
            graphs.append(graph_item)

        return ("", mp_code, scope, selected_index, scale, x_slider, y_slider,
                graphs)

    except Exception as e:
        status = "Error reading Gryphon file '%s': %s" % (
                                         gry_filename, str(e))
        return (status, "", 1, 0, 1, 0, 0, list())

# export JSON graph Gryphon file.  Return (status)
def export_gry_file(gry_filename, mp_code_text, scope,
                   selected_index, scale, x_slider, y_slider, graphs):

    json_multigraph = dict()
    json_multigraph["mp_code"] = mp_code_text
    json_multigraph["scope"] = scope
    json_multigraph["selected_index"] = selected_index
    json_multigraph["scale"] = scale
    json_multigraph["x_slider"] = x_slider
    json_multigraph["y_slider"] = y_slider

    # prepare graphs list
    json_graphs = list()
    for graph_item in graphs:

        # make sure the graph_item is initialized, specifically, edge.cbp1
        # and edge.cbp2 must be set
        graph_item.initialize_items()

        # populate the data structure for this graph
        json_graph = dict()
#        json_graph["directed"] = True
#        json_graph["type"] = ""
#        json_graph["label"] = ""
        json_graph["index"] = graph_item.index
        json_graph["mark"] = graph_item.mark
        json_graph["probability"] = graph_item.probability
        json_nodes = list()
        json_edges = list()
        for node in graph_item.nodes:
            json_node = dict()
            json_node["id"] = node.node_id
            json_node["type"] = node.node_type
            json_node["label"] = node.label
            json_node["x"] = node.x()
            json_node["y"] = node.y()
            json_node["hide"] = node.hide
            json_node["collapse"] = node.collapse
            json_node["collapse_below"] = node.collapse_below
            json_nodes.append(json_node)

        for edge in graph_item.edges:
            json_edge = dict()
            json_edge["source"] = edge.source_id
            json_edge["relation"] = edge.relation
            json_edge["target"] = edge.target_id
            json_edge["label"] = edge.label
            json_edge["cbp1_x"] = edge.cbp1.x()
            json_edge["cbp1_y"] = edge.cbp1.y()
            json_edge["cbp2_x"] = edge.cbp2.x()
            json_edge["cbp2_y"] = edge.cbp2.y()
            json_edges.append(json_edge)

        json_graph["nodes"] = json_nodes
        json_graph["edges"] = json_edges
        json_graphs.append(json_graph)
    json_multigraph["graphs"] = json_graphs

    # export the JSON multigraph Gryphon file
    try:
        with open(gry_filename, "w") as f:
            json.dump(json_multigraph, f, indent=4, sort_keys=4)
        return ""

    except Exception as e:
        status = "Error exporting Gryphon file '%s': %s" % (
                                         gry_filename, str(e))
        return (status)

