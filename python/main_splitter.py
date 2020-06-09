from PyQt5.QtCore import pyqtSignal # for signal/slot support
from PyQt5.QtCore import pyqtSlot # for signal/slot support
from PyQt5.QtWidgets import QSplitter

"""The main splitter containing the graphs list, main graph, code_column.

Signals:
  * signal_graph_list_width_changed(int) - width of graph list changed
"""

class MainSplitter(QSplitter):

    # signals
    signal_graph_list_width_changed = pyqtSignal(int,
                                      name='graphListWidthChanged')

    def __init__(self, graph_list_width_manager):
        super(MainSplitter, self).__init__()
        self.graph_list_width_manager = graph_list_width_manager
        self.splitterMoved.connect(self.splitter_bar_moved)

    # QSplitter resize
    def resizeEvent(self, e):
        super(MainSplitter, self).resizeEvent(e)
        self.graph_list_width_manager.set_width(self.sizes()[2])

    # QSplitter splitter bar moved
    @pyqtSlot(int, int)
    def splitter_bar_moved(self, pos, index):
        self.graph_list_width_manager.set_width(self.sizes()[2])

