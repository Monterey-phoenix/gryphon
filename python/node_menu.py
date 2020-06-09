from PyQt5.QtCore import QObject # for signal/slot support
from PyQt5.QtCore import pyqtSlot # for signal/slot support
from PyQt5.QtWidgets import QMenu
from PyQt5.QtWidgets import QAction
from PyQt5.QtGui import QCursor
from collapse_helpers import collapse_below, uncollapse_below

class NodeMenu(QObject):

    def __init__(self):
        super(NodeMenu, self).__init__()

        self.graph_item = None
        self.node = None

        # actions
        # collapse
        self.action_collapse = QAction("Collapse")
        self.action_collapse.setStatusTip("Collapse events under this event")
        self.action_collapse.triggered.connect(self.do_collapse)
        # uncollapse
        self.action_uncollapse = QAction("Expand")
        self.action_uncollapse.setStatusTip("Expand events under this event")
        self.action_uncollapse.triggered.connect(self.do_uncollapse)
        # hide
        self.action_hide = QAction("Hide")
        self.action_hide.setStatusTip("Hide this event")
        self.action_hide.triggered.connect(self.do_hide)
        # unhide
        self.action_unhide = QAction("Show")
        self.action_unhide.setStatusTip("Show this event")
        self.action_unhide.triggered.connect(self.do_unhide)

        self.menu = QMenu()
        self.menu.addAction(self.action_collapse)
        self.menu.addAction(self.action_uncollapse)
        self.menu.addAction(self.action_hide)
        self.menu.addAction(self.action_unhide)

    def show_menu(self, graph_item, node):
        self.graph_item = graph_item
        self.node = node

        # Root, Composite, Schema, not atomic(A) or say(T)
        can_collapse = node.node_type == "R" or node.node_type == "C" or \
                       node.node_type == "S"
        if can_collapse:
            self.action_collapse.setEnabled(not node.collapse_below)
            self.action_uncollapse.setEnabled(node.collapse_below)
        else:
            self.action_collapse.setEnabled(False)
            self.action_uncollapse.setEnabled(False)
        self.action_hide.setEnabled(not node.hide)
        self.action_unhide.setEnabled(node.hide)

        action = self.menu.exec(QCursor.pos())

    def do_collapse(self):
        collapse_below(self.node)
        self.graph_item.set_collapsed_edges()

    def do_uncollapse(self):
        uncollapse_below(self.node)
        self.graph_item.set_collapsed_edges()

    def do_hide(self):
        self.node.hide = True
        self.node.set_appearance()
        for edge in self.node.edge_list:
            edge.set_appearance()

    def do_unhide(self):
        self.node.hide = False
        self.node.set_appearance()
        for edge in self.node.edge_list:
            edge.set_appearance()

