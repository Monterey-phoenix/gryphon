
#
# Modification History:
#   180803 David Shifflett
#     Switched to rectangular area graph object selection
#     Changed scrollbars to remain constant on zoom
#

# Adapted from https://raw.githubusercontent.com/baoboa/pyqt5/master/examples/graphicsview/elasticnodes.py

import math
from PyQt5.QtCore import (QLineF, QPointF, qrand, QRect, QRectF, QSizeF, Qt)
from PyQt5.QtCore import QPoint
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtCore import QObject
from PyQt5.QtGui import (QBrush, QColor, QLinearGradient, QPainter,
                         QPainterPath, QPen, QPolygonF, QRadialGradient)
from PyQt5.QtGui import QTransform
from PyQt5.QtWidgets import (QGraphicsItem, QGraphicsView, QStyle)
from PyQt5.QtWidgets import QGraphicsScene
from graph_constants import graphics_rect
from graph_item import GraphItem
from settings_manager import settings
from graph_collapse_helpers import collapse_below, uncollapse_below
#from node import Node # for Node detection
from edge_grip import EdgeGrip

"""GraphMainWidget provides the main QGraphicsView.  It manages signals
and wraps these:
  * GraphMainView
  * GraphMainScene

GraphMainWidget also issues signal:
  * signal_graph_item_view_changed = pyqtSignal(GraphItem,
                                                name='graphItemViewChanged')
"""

# GraphicsView
class GraphMainView(QGraphicsView):
    def __init__(self):
        super(GraphMainView, self).__init__()

        self.viewport_cursor = Qt.ArrowCursor
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setRenderHint(QPainter.Antialiasing)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)

        # enable user rectangular selection
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.viewport().setCursor(self.viewport_cursor)
        self.setSceneRect(graphics_rect)
        self.setMinimumSize(300, 300)

    # Manage restorable scaling using scale_value, _rescale,
    # reset_view_orientation, and set_view_orientation.
    # It seems we need to store scale_value because QTransform cannot poll it.
    # set scale to value
    def _set_scale(self, scale_value):
        self.setTransform(QTransform())
        self._scale_value = scale_value
        self.scale(scale_value, scale_value)

    # _rescale by scale factor
    def _rescale(self, scale_factor):
        self.scale(scale_factor, scale_factor)
        self._scale_value *= scale_factor

    # reset viewport view to starting orientation
    def reset_view_orientation(self):
        self.setTransform(QTransform())
        self._set_scale(1.0)
        self.centerOn(0, 0)

    # set viewport view to specific orientation
    def set_view_orientation(self, scale_value, x_slider, y_slider):
        self.setTransform(QTransform())
        self._set_scale(scale_value)
        self.horizontalScrollBar().setValue(x_slider)
        self.verticalScrollBar().setValue(y_slider)

    # poll specific view orientation
    # return scale, x_slider, y_slider
    def get_view_orientation(self):
        return (self._scale_value, 
                self.horizontalScrollBar().value(),
                self.verticalScrollBar().value())

    # select all nodes
    def select_all(self):
        graph_item = self.scene().graph_item
        if graph_item:
            for node in graph_item.nodes:
                node.setSelected(True)

            # clear any edge grips
            self.scene().clear_grips()

    # toggle hide/unhide on selected nodes
    def toggle_hide_unhide(self):
        graph_item = self.scene().graph_item
        if graph_item:
            for node in graph_item.nodes:
                if node.isSelected():
                    node.hide = not node.hide

                    # set appearance on changed node
                    node.set_appearance()

            # simpler to set appearance on all edges
            for edge in graph_item.edges:
                edge.set_appearance()

    # toggle collapse/uncollapse on selected Root and Composite nodes
    def toggle_collapse_uncollapse(self):
        graph_item = self.scene().graph_item
        if graph_item:
            for node in graph_item.nodes:
                if node.isSelected():
                    if node.node_type == "R" or node.node_type == "C":
                        if node.collapse_below:
                            uncollapse_below(node)
                        else:
                            collapse_below(node)

            graph_item.set_collapsed_edges()

    def keyPressEvent(self, event):

        # keystroke controls
        key = event.key()
        v = self.verticalScrollBar().value()
        h = self.horizontalScrollBar().value()

        if key == Qt.Key_Up:
            self.verticalScrollBar().setValue(v-20)
        elif key == Qt.Key_Down:
            self.verticalScrollBar().setValue(v+20)
        elif key == Qt.Key_Left:
            self.horizontalScrollBar().setValue(h-20)
        elif key == Qt.Key_Right:
            self.horizontalScrollBar().setValue(h+20)
        elif key == Qt.Key_Plus:
            self.scale_view(1.2)
        elif key == Qt.Key_Minus:
            self.scale_view(1 / 1.2)
        elif key == Qt.Key_Space or key == Qt.Key_Enter:
            pass
        elif key == Qt.Key_A and event.modifiers() == Qt.ControlModifier:
            self.select_all()
        elif key == Qt.Key_H:
            self.toggle_hide_unhide()
        elif key == Qt.Key_C:
            self.toggle_collapse_uncollapse()

        else:
            super(GraphMainView, self).keyPressEvent(event)

    def mousePressEvent(self, event):
        # view mode
        if event.button() == Qt.LeftButton and \
                      event.modifiers() & Qt.ShiftModifier == Qt.ShiftModifier:
            self.setDragMode(QGraphicsView.RubberBandDrag)
            self.viewport().setCursor(self.viewport_cursor)

        super(GraphMainView, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        # view mode
        super(GraphMainView, self).mouseReleaseEvent(event)

        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.viewport().setCursor(self.viewport_cursor)

    def wheelEvent(self, event):
        self.scale_view(1.0/(math.pow(2.0, -event.angleDelta().y() / 240.0)))

    def drawBackground(self, painter, rect):
        # Shadow.
        sceneRect = self.sceneRect()
        rightShadow = QRectF(sceneRect.right(), sceneRect.top() + 5, 5,
                sceneRect.height())
        bottomShadow = QRectF(sceneRect.left() + 5, sceneRect.bottom(),
                sceneRect.width(), 5)
        if rightShadow.intersects(rect) or rightShadow.contains(rect):
	        painter.fillRect(rightShadow, Qt.darkGray)
        if bottomShadow.intersects(rect) or bottomShadow.contains(rect):
	        painter.fillRect(bottomShadow, Qt.darkGray)

        # Fill.
        gradient = QLinearGradient(sceneRect.topLeft(), sceneRect.bottomRight())
        c = QColor(settings["graph_background_c"])
        gradient.setColorAt(0, c.lighter(settings["graph_gradient"]))
        gradient.setColorAt(0.5, c)
        gradient.setColorAt(1, c.darker(settings["graph_gradient"]))
        painter.fillRect(rect.intersected(sceneRect), QBrush(gradient))
        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(Qt.black, 0))
        painter.drawRect(sceneRect)

    def scale_view(self, scaleFactor):
        # cache the scrollbar position
        h_slider = self.horizontalScrollBar().value()
        v_slider = self.verticalScrollBar().value()

        self._rescale(scaleFactor)

        # keep the scrollbars at the previous position
        self.horizontalScrollBar().setValue(h_slider)
        self.verticalScrollBar().setValue(v_slider)

class GraphMainScene(QGraphicsScene):

    def __init__(self):
        super(GraphMainScene, self).__init__()
        self.graph_item = None

        # edge grips
        self.source_edge_grip = EdgeGrip("source")
        self.dest_edge_grip = EdgeGrip("dest")

    # set_scene
    def set_scene(self, graph_item):
        self.clear_scene()

        # keep for metadata
        self.graph_item = graph_item

        # optimization: just-in-time for display, see graph_item.py
        graph_item.initialize_items()
        graph_item.set_appearance()

        # add node items
        for node in graph_item.nodes:
            self.addItem(node)

        # add edge items
        for edge in graph_item.edges:
            self.addItem(edge)

        # add edge grips
        self.addItem(self.source_edge_grip)
        self.addItem(self.dest_edge_grip)

    # clear_scene
    def clear_scene(self):
        # turn off grip selection and grips
        self.clear_grips()

        # we must call removeItem so QGraphicsScene does not delete these
        for item in self.items():
            self.removeItem(item)

        # clear graph_item pointer
        self.graph_item = None

        # hack to remove cached residue from edges
        self.clear()

    def clear_grips(self):
        if self.graph_item:
            # turn off any previous edge grip selection
            for edge in self.graph_item.edges:
                if edge.show_grips:
                    edge.show_grips = False
                    edge.set_appearance()

            # turn off any grips
            self.source_edge_grip.clear_grip()
            self.dest_edge_grip.clear_grip()

    def show_grips(self, edge):
        self.clear_grips()
        edge.show_grips = True
        edge.set_appearance()
        self.source_edge_grip.show_grip(edge)
        self.dest_edge_grip.show_grip(edge)

    def mousePressEvent(self, event):
        # if down click happens and not over grip then turn off grips
        g1 = self.source_edge_grip
        g2 = self.dest_edge_grip
        if not ((g1.isUnderMouse() and g1.isVisible()) or 
                (g2.isUnderMouse() and g2.isVisible())):
            self.clear_grips()
        super(GraphMainScene, self).mousePressEvent(event)

# GraphMainWidget
class GraphMainWidget(QObject):

    # signals
    signal_graph_item_view_changed = pyqtSignal(GraphItem,
                                                name='graphViewChanged')

    def __init__(self, graphs_manager, graph_list_widget):
        super(GraphMainWidget, self).__init__()

        # GraphMainWidget's scene and view objects
        self.scene = GraphMainScene()
        self.view = GraphMainView()
        self.view.setScene(self.scene)

        # connect to clear main scene when graph list is loaded
        graphs_manager.signal_graphs_loaded.connect(self.scene.clear_scene)

        # connect to set main scene on graph_list_widget selection
        graph_list_widget.signal_graph_selection_changed.connect(
                                                    self.scene.set_scene)

        # connect to know when graph_item geometry changes in order to
        # emit need to repaint
        self.scene.changed.connect(self.changed_main_view)

        # connect to schedule repaint when graph appearance changes
        graphs_manager.signal_appearance_changed.connect(self.change_appearance)

    # reset viewport view to starting orientation
    def reset_view_orientation(self):
        self.view.reset_view_orientation()

    # set viewport view to specific orientation
    def set_view_orientation(self, scale_value, x_slider, y_slider):
        self.view.set_view_orientation(scale_value, x_slider, y_slider)

    # poll specific view orientation, return scale, x_slider, y_slider
    def get_view_orientation(self):
        return self.view.get_view_orientation()

    # call this to emit indication that the main view geometry changed somehow
    @pyqtSlot('QList<QRectF>')
    def changed_main_view(self, region):
        if self.scene.graph_item:
            self.signal_graph_item_view_changed.emit(self.scene.graph_item)

    # call this to accept appearance change
    @pyqtSlot()
    def change_appearance(self):
        # change the graph
        if self.scene.graph_item:
            self.scene.graph_item.set_appearance()
        else:
            # no graph so force background update directly
            self.scene.update()

