from PyQt5.QtCore import QRect
from graph_constants import graphics_rect
from graph_collapse_helpers import collapsed_edges
from edge import Edge
from edge_point_placer import EdgePointPlacer

"""Defines one graph item.
Data structures:
  * index (int)
  * mark (str)
  * nodes (list<Node>)
  * edges (list<Edge>)

NOTE: Optimization: call initialize_items and appearance just-in-time.
Set appearance when graph should be painted differently.
"""

class GraphItem():

    def __init__(self, index, mark, probability, nodes, edges):
        super(GraphItem, self).__init__()

        self.index = index
        self.mark = mark
        self.probability = probability
        self.nodes = nodes
        self.edges = edges

        self._items_initialized = False
        self.appearance_set = False

    # perform orderly just-in-time initialization of graph item components
    def initialize_items(self):
        if not self._items_initialized:
            # initialize items
            for node in self.nodes:
                node.initialize_node(self)
            placer = EdgePointPlacer()
            for edge in self.edges:
                edge.initialize_edge(placer)
            self._items_initialized = True

    # reset appearance when graph color or shape changes
    def set_appearance(self):
        if not self.appearance_set:
            for node in self.nodes:
                node.set_appearance()
            for edge in self.edges:
                edge.set_appearance()
            self.appearance_set = True

    def change_h_spacing(self, old_spacing, old_indent,
                               new_spacing, new_indent):
        for node in self.nodes:
            x = (node.x() - old_indent) / old_spacing * new_spacing + new_indent
            node.setPos(x, node.y())
            
    def change_v_spacing(self, old_spacing, old_indent,
                               new_spacing, new_indent):
        for node in self.nodes:
            y = (node.y() - old_indent) / old_spacing * new_spacing + new_indent
            node.setPos(node.x(), y)

    def bounding_rect(self):
        # perform any just-in-time initialization
        self.initialize_items()
        self.set_appearance()

        # find the corners of this graph
        min_x = graphics_rect.x() + graphics_rect.width()
        max_x = graphics_rect.x()
        min_y = graphics_rect.y() + graphics_rect.height()
        max_y = graphics_rect.y()
        for node in self.nodes:
           if node.x() - node.w/2 < min_x:
               min_x = node.x() - node.w/2
           if node.x() + node.w/2 > max_x:
               max_x = node.x() + node.w/2
           if node.y() - node.h/2 < min_y:
               min_y = node.y() - node.h/2
           if node.y() + node.h/2 > max_y:
               max_y = node.y() + node.h/2

        return QRect(min_x, min_y, max_x-min_x, max_y-min_y)

    # uncollapse all nodes of node type
    def uncollapse(self, node_type):
        for node in self.nodes:
            if node.node_type == node_type:
                node.do_uncollapse()
        self.appearance_set = False
        self.set_appearance()
        self.set_collapsed_edges()

    # diagnostics
    def _print_totals(self):
        if not len(self.edges):
            print("Totals: None, empty graph.")
            return

        # total items in QGraphicsScene
        graph_main_scene = self.edges[0].scene()
        scene_item_total = len(graph_main_scene.items())

        # nodes + edges in this graph_item
        graph_item_total = len(self.nodes) + len(self.edges)

        # edge_list_total
        edge_list_total = 0
        for node in self.nodes:
            edge_list_total += len(node.edge_list)

        print("Totals: scene: %d, graph: %d, graph nodes: %d, graph edges: %d, edge list total: %d" % (scene_item_total, graph_item_total, len(self.nodes), len(self.edges), edge_list_total))

    # redo the list of collapsed edges in edges[] based on what is collapsed
    def set_collapsed_edges(self):
        print("set_collapsed_edges.a")
        self._print_totals()
        removable_edges, addable_edge_pairs = collapsed_edges(self)

        # a reference to node_lookup
        node_lookup = self.edges[0].node_lookup

        # create the addable edges
        addable_edges = list()
        for source_node, dest_node in addable_edge_pairs:
            addable_edge = Edge(source_node.node_id, "COLLAPSED_FOLLOWS",
                                dest_node.node_id, "", node_lookup)
            addable_edges.append(addable_edge)

        # remove any discontinued FOLLOWS edges
        for removable_edge in removable_edges:
            removable_edge.source_node.edge_list.remove(removable_edge)
            removable_edge.dest_node.edge_list.remove(removable_edge)
            self.edges.remove(removable_edge)

        # add any new FOLLOWS edges
        placer = EdgePointPlacer()
        for addable_edge in addable_edges:
            self.edges.append(addable_edge)
            addable_edge.initialize_edge(placer)
            addable_edge.set_appearance()

        # change the COLLAPSED_FOLLOWS edges in graph_main_widget
        # get graph main scene
        graph_main_scene = self.edges[0].scene()
#        graph_main_scene.change_collapsed_edges(removable_edges, addable_edges)

        graph_main_scene.clear_scene()
        graph_main_scene.set_scene(self)

        # reset appearance
        self.appearance_set = False
        self.set_appearance()

        print("set_collapsed_edges.b")
        self._print_totals()

