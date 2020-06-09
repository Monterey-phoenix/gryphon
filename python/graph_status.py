
#
# Modification History:
#   180803 David Shifflett
#     Moved trace number display, and # of traces into trace_navigation class
#

from PyQt5.QtCore import QObject # for signal/slot support
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QLabel

"""Provides status text for the graph traces."""
class GraphStatus(QObject):

    def __init__(self, graphs_manager):
        super(GraphStatus, self).__init__()

        self.graphs_manager = graphs_manager

        # connect
        graphs_manager.signal_graphs_loaded.connect(self.set_graph_metadata)

        # the status text
        self.status_text = QLabel()

        # cached state
        self.schema_name = graphs_manager.schema_name
        self.scope = graphs_manager.scope

    def set_text(self):
        self.status_text.setText("%s   Scope %d" % (
                                 self.schema_name,
                                 self.scope))

    @pyqtSlot()
    def set_graph_metadata(self):
        self.schema_name = self.graphs_manager.schema_name
        self.scope = self.graphs_manager.scope
        self.set_text()

