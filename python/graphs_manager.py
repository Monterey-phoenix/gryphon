from PyQt5.QtCore import QObject # for signal/slot support
from PyQt5.QtCore import pyqtSignal # for signal/slot support
from PyQt5.QtCore import pyqtSlot # for signal/slot support
from PyQt5.QtCore import QPointF # for node location float
"""Provides graphs (list<GraphItem>) and signals when the graph list
is loaded or cleared.

Register with signal_graphs_loaded to provide current graph list.

Data structures:
  * schema_name (str)
  * scope (int)
  * graphs (list<GraphItem>)

Signals:
  * signal_graphs_loaded() - graphs were loaded or cleared
  * signal_appearance_changed() - graph appearance changed
"""

class GraphsManager(QObject):

    # signals
    signal_graphs_loaded = pyqtSignal(name='graphsLoaded')
    signal_appearance_changed = pyqtSignal(name='appearanceChanged')

    def __init__(self, settings_manager):
        super(GraphsManager, self).__init__()

        # set initial state
        self.clear_graphs()

        # accept graph changes and signal appearance changed 
        settings_manager.signal_settings_changed.connect(
                                               self.appearance_changed)

    def set_graphs(self, schema_name, scope, graphs):
        self.schema_name = schema_name
        self.scope = scope
        self.graphs = graphs
        self.signal_graphs_loaded.emit()

    def clear_graphs(self):
        self.schema_name = "Schema not defined"
        self.scope = 0
        self.graphs = list()
        self.signal_graphs_loaded.emit()

    @pyqtSlot(dict, dict)
    def appearance_changed(self, old_settings, new_settings):
        # make all graphs need appearance_set
        for graph in self.graphs:
            graph.appearance_set = False

        # maybe change spacing
        if old_settings["graph_h_spacing"] != new_settings["graph_h_spacing"]:
            for graph in self.graphs:
                graph.change_h_spacing(old_settings["graph_h_spacing"],
                                       old_settings["node_width"]/2,
                                       new_settings["graph_h_spacing"],
                                       new_settings["node_width"]/2)
        if old_settings["graph_v_spacing"] != new_settings["graph_v_spacing"]:
            for graph in self.graphs:
                graph.change_v_spacing(old_settings["graph_v_spacing"],
                                       old_settings["node_height"]/2,
                                       new_settings["graph_v_spacing"],
                                       new_settings["node_height"]/2)

        # signal change
        self.signal_appearance_changed.emit()

    # return graph associated with graph_index else None
    def find_graph(self, graph_index):
        for graph in self.graphs:
            if graph.index == graph_index:
                # return subscript
                return graph
        # not found
        return None

