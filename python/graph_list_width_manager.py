from PyQt5.QtCore import QObject # for signal/slot support
from PyQt5.QtCore import pyqtSignal # for signal/slot support
from PyQt5.QtCore import pyqtSlot # for signal/slot support

"""Track graph list width and signal change

Data:
  * width - width of the graph list available in the list splitpane

Signals:
  * signal_graph_list_width_changed(int) - width of graph list changed
"""

class GraphListWidthManager(QObject):

    # signals
    signal_graph_list_width_changed = pyqtSignal(int,
                                      name='graphListWidthChanged')

    def __init__(self, scrollbar_width):
        super(GraphListWidthManager, self).__init__()
        self.scrollbar_width = scrollbar_width
        self.width = None

    # call this to set width
    def set_width(self, width):
        self.width = width
        self.signal_graph_list_width_changed.emit(width)

