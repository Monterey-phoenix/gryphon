from PyQt5.QtCore import Qt # for Vertical
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QSplitter

class GraphListColumn(QWidget):
    """Container for trace navigation and graph list
    """

    def __init__(self, gui_manager):
        super(GraphListColumn, self).__init__()

        vlayout = QVBoxLayout()
        vlayout.setContentsMargins(0, 0, 0, 0)
        self.splitter = QSplitter(Qt.Vertical)
        vlayout.addWidget(self.splitter)

        # trace navigation
        self.splitter.addWidget(gui_manager.trace_navigation)

        # graph list editor
        self.splitter.addWidget(gui_manager.graph_list_widget.view)

        # now set layout
        self.setLayout(vlayout)

    # set split sizes
    def set_sizes(self, sizes):
        self.splitter.setSizes(sizes)

