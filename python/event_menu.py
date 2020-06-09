from PyQt5.QtCore import QObject # for signal/slot support
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QMenu
from PyQt5.QtWidgets import QAction
from PyQt5.QtGui import QIcon
from graph_collapse_helpers import collapse_below, uncollapse_below
from graph_item import GraphItem

"""Provides event_menu."""

class EventMenu(QObject):

    def __init__(self, graphs_manager, graph_list_widget, settings_manager):
        super(EventMenu, self).__init__()

        self.graphs_manager = graphs_manager
        self.settings_manager = settings_manager

        # connect
        graphs_manager.signal_graphs_loaded.connect(self.set_graph_metadata)
        graph_list_widget.signal_graph_selection_changed.connect(
                                                    self.set_graph_selection)

        # cached state
        self.selected_graph_item = None

        # The event_menu
        self.event_menu = QMenu()
        self.event_menu.aboutToShow.connect(self._set_menu_visibility)

        # unhide all events
        self.action_unhide = QAction("Show Hidden Events")
        self.action_unhide.setStatusTip("Stop hiding all hidden events")
        self.action_unhide.triggered.connect(self.do_unhide)

        # collapse all root events
        self.action_collapse_roots = QAction("Collapse Root Events")
        self.action_collapse_roots.setStatusTip("Collapse all Root events")
        self.action_collapse_roots.triggered.connect(self.do_collapse_roots)

        # uncollapse all root events
        self.action_uncollapse_roots = QAction("Expand Root Events")
        self.action_uncollapse_roots.setStatusTip("Expand all collapsed Root events")
        self.action_uncollapse_roots.triggered.connect(self.do_uncollapse_roots)

        # collapse all composite events
        self.action_collapse_composites = QAction("Collapse Composite Events")
        self.action_collapse_composites.setStatusTip(
                                              "Collapse all Composite events")
        self.action_collapse_composites.triggered.connect(
                                              self.do_collapse_composites)

        # uncollapse all composite events
        self.action_uncollapse_composites = QAction(
                                              "Expand Composite Events")
        self.action_uncollapse_composites.setStatusTip(
                                              "Expand all collapsed Composite events")
        self.action_uncollapse_composites.triggered.connect(
                                              self.do_uncollapse_composites)

        # 0% opacity
        self.action_opacity_0 = QAction("0% (completely transparent)")
        self.action_opacity_0.triggered.connect(self.do_opacity_0)

        # 25% opacity
        self.action_opacity_25 = QAction("25%")
        self.action_opacity_25.triggered.connect(self.do_opacity_25)

        # 50% opacity
        self.action_opacity_50 = QAction("50%")
        self.action_opacity_50.triggered.connect(self.do_opacity_50)

        # 75% opacity
        self.action_opacity_75 = QAction("75%")
        self.action_opacity_75.triggered.connect(self.do_opacity_75)

        # populate event_menu
        self.event_menu.addAction(self.action_unhide)
        self.event_menu.addSeparator()
        self.event_menu.addAction(self.action_collapse_roots)
        self.event_menu.addAction(self.action_uncollapse_roots)
        self.event_menu.addSeparator()
        self.event_menu.addAction(self.action_collapse_composites)
        self.event_menu.addAction(self.action_uncollapse_composites)
        self.event_menu.addSeparator()
        self.opacity_menu = self.event_menu.addMenu("Hidden/collapsed &opacity")
        self.opacity_menu.addAction(self.action_opacity_0)
        self.opacity_menu.addAction(self.action_opacity_25)
        self.opacity_menu.addAction(self.action_opacity_50)
        self.opacity_menu.addAction(self.action_opacity_75)

    def _set_menu_visibility(self):
        # no graph
        if not self.selected_graph_item:
            self.action_unhide.setEnabled(False)
            self.action_collapse_roots.setEnabled(False)
            self.action_uncollapse_roots.setEnabled(False)
            self.action_collapse_composites.setEnabled(False)
            self.action_uncollapse_composites.setEnabled(False)
            return

        # see what can be done
        can_unhide = False
        can_collapse_roots = False
        can_uncollapse_roots = False
        can_collapse_composites = False
        can_uncollapse_composites = False
        if self.selected_graph_item:
            for node in self.selected_graph_item.nodes:
                if node.hide:
                    can_unhide = True
                if node.node_type == "R" and node.collapse_below == False:
                    can_collapse_roots = True
                if node.node_type == "R" and node.collapse_below:
                    can_uncollapse_roots = True
                if node.node_type == "C" and node.collapse_below == False:
                    can_collapse_composites = True
                if node.node_type == "C" and node.collapse_below:
                    can_uncollapse_composites = True

        # enable visibility based on what can be done
        self.action_unhide.setEnabled(can_unhide)
        self.action_collapse_roots.setEnabled(can_collapse_roots)
        self.action_uncollapse_roots.setEnabled(can_uncollapse_roots)
        self.action_collapse_composites.setEnabled(can_collapse_composites)
        self.action_uncollapse_composites.setEnabled(can_uncollapse_composites)

    @pyqtSlot()
    def set_graph_metadata(self):
        self.selected_graph_item = None

    @pyqtSlot(GraphItem)
    def set_graph_selection(self, graph_item):
        self.selected_graph_item = graph_item

    @pyqtSlot()
    def do_unhide(self):
        for node in self.selected_graph_item.nodes:
            if node.hide:
                node.hide = False
                node.set_appearance()

    @pyqtSlot()
    def do_collapse_roots(self):
        for node in self.selected_graph_item.nodes:
            if node.node_type == "R" and not node.collapse_below:
                collapse_below(node)
        self.selected_graph_item.set_collapsed_edges()

    @pyqtSlot()
    def do_uncollapse_roots(self):
        for node in self.selected_graph_item.nodes:
            if node.node_type == "R" and node.collapse_below:
                uncollapse_below(node)
        self.selected_graph_item.set_collapsed_edges()

    @pyqtSlot()
    def do_collapse_composites(self):
        for node in self.selected_graph_item.nodes:
            if node.node_type == "C" and not node.collapse_below:
                collapse_below(node)
        self.selected_graph_item.set_collapsed_edges()

    @pyqtSlot()
    def do_uncollapse_composites(self):
        for node in self.selected_graph_item.nodes:
            if node.node_type == "C" and node.collapse_below:
                uncollapse_below(node)
        self.selected_graph_item.set_collapsed_edges()

    @pyqtSlot()
    def do_opacity_0(self):
        self.settings_manager.change({"graph_hide_collapse_opacity":0})

    @pyqtSlot()
    def do_opacity_25(self):
        self.settings_manager.change({"graph_hide_collapse_opacity":63})

    @pyqtSlot()
    def do_opacity_50(self):
        self.settings_manager.change({"graph_hide_collapse_opacity":127})

    @pyqtSlot()
    def do_opacity_75(self):
        self.settings_manager.change({"graph_hide_collapse_opacity":191})

