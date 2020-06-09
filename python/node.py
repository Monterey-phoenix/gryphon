# Adapted from https://raw.githubusercontent.com/baoboa/pyqt5/master/examples/graphicsview/elasticnodes.py

from PyQt5.QtCore import QPointF, QRectF
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtCore import Qt
from PyQt5.QtGui import (QBrush, QColor, QLinearGradient, QPainter,
                         QPainterPath, QPen, QPolygonF, QRadialGradient)
from PyQt5.QtGui import QTransform
from PyQt5.QtGui import QPolygonF
from PyQt5.QtGui import QFontMetrics
from PyQt5.QtGui import QFont
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import (QGraphicsItem, QGraphicsView, QStyle)
from PyQt5.QtWidgets import QGraphicsSceneContextMenuEvent
from graph_constants import graphics_rect
from settings_manager import settings
from graph_collapse_helpers import at_and_below_in
from node_menu import NodeMenu

# Node
class Node(QGraphicsItem):
    Type = QGraphicsItem.UserType + 1

    def __init__(self, node_id, node_type, label, x, y,
                                        hide, collapse, collapse_below):
        super(Node, self).__init__()

        # MP attributes
        self.node_id = node_id  # retain for export
        self.node_type = node_type
        self.label = label
        self.setPos(QPointF(x,y))
        self.hide = hide
        self.collapse = collapse
        self.collapse_below = collapse_below

    # optimization: just-in-time for display, see graph_item.py
    def initialize_node(self, graph_item):

        # graphicsItem mode
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setZValue(1)

        # MP graph attributes
        self.edge_list = []

        # handle back for menus
        self.graph_item = graph_item

    # adjust for appearance change
    def set_appearance(self):
        self.w = settings["node_width"]
        self.h = settings["node_height"]
        self.s = 3  # shadow size
        self.t = 12  # tab fold size
        self.node_border = settings["node_border"]
        self.node_shadow = settings["node_shadow"]

        # set opacity
        if self.hide or self.collapse:
            self.opacity = settings["graph_hide_collapse_opacity"]
        else:
            # totally opaque
            self.opacity = 255

        # set gradient between upper-left and lower-right
        self.gradient = QLinearGradient(-self.w/2, -self.h/2,
                                        self.w/2, self.h/2)

        # increase node height if node's label does not fit
        fm = QFontMetrics(QFont()) # use default font since we do not set it
        rect = fm.boundingRect(0,0,self.w, self.h+100,
                               Qt.TextWordWrap, self.label)
        if rect.height() > self.h:
            self.h = rect.height()

        # path region for mouse detection
        self.mouse_path = QPainterPath()
        self.mouse_path.addRect(-self.w/2, -self.h/2, self.w, self.h)

        # define the graphics view bounds for this node
        self.min_x = graphics_rect.x() + self.w/2
        self.max_x = graphics_rect.width() + graphics_rect.x() - self.w/2
        self.min_y = graphics_rect.y() + self.h/2
        self.max_y = graphics_rect.height()+ graphics_rect.y() - self.h/2

        # define decoration for this node
        self.right_shadow = QRectF(self.w/2, -self.h/2+self.s, self.s, self.h)
        # CW from upper-left
        self.right_shadow_say = QPolygonF(
                          [QPointF(+self.w/2, -self.h/2+self.t),
                           QPointF(+self.w/2+self.s, -self.h/2+self.t+self.s),
                           QPointF(+self.w/2+self.s, +self.h/2+self.s),
                           QPointF(+self.w/2,   +self.h/2+self.s)])
        self.bottom_shadow = QRectF(-self.w/2+self.s, self.h/2, self.w, self.s)
        self.box = QRectF(-self.w/2, -self.h/2, self.w, self.h)
        # CW from upper-left
        self.tbox = QPolygonF([QPointF(-self.w/2,   -self.h/2  ),
                               QPointF(+self.w/2-self.t, -self.h/2  ),
                               QPointF(+self.w/2,   -self.h/2+self.t),
                               QPointF(+self.w/2,   +self.h/2  ),
                               QPointF(-self.w/2,   +self.h/2  )])
        self.tbox_inset = QPolygonF([QPointF(self.w/2-self.t, -self.h/2),
                                     QPointF(self.w/2-self.t, -self.h/2+self.t),
                                     QPointF(self.w/2, -self.h/2+self.t)])

        # background color
        if self.node_type == "R": # root
            c = QColor(settings["node_root_c"])
        elif self.node_type == "A": # atomic
            c = QColor(settings["node_atomic_c"])
        elif self.node_type == "C": # composite
            c = QColor(settings["node_composite_c"])
        elif self.node_type == "S": # schema
            c = QColor(settings["node_schema_c"])
        elif self.node_type == "T": # say
            c = QColor(settings["node_say_c"])
        else:
            print("unrecognized node type '%s'" % self.node_type)
            c = Qt.darkGray
        # opacity
        c.setAlpha(self.opacity)
        self.c1 = c.lighter(settings["graph_gradient"])
        self.c2 = c
        self.c3 = c.darker(settings["graph_gradient"])

        # annotation color
        if self.isSelected():
            c = self.c2.lighter(140)
        else:
            c = self.c2
        # brightness from https://stackoverflow.com/questions/3942878/how-to-decide-font-color-in-white-or-black-depending-on-background-color
        brightness = 0.299*c.red()+0.587*c.green()+0.114*c.blue()
        if brightness > settings["node_t_contrast"]:
            self.annotation_color = QColor(Qt.black)
        else:
            self.annotation_color = QColor(Qt.white)
        self.annotation_color.setAlpha(self.opacity)

        # menu icon color
        self.menu_icon_color = QColor(Qt.black)
        self.menu_icon_color.setAlpha(self.opacity)

        # border color
        self.border_color = QColor(Qt.black)
        self.border_color.setAlpha(self.opacity)

        # shadow color
        self.shadow_color = QColor(Qt.darkGray)
        self.shadow_color.setAlpha(self.opacity)

        # collapse_below color
        self.collapse_below_color = QColor(Qt.darkGray)
        self.collapse_below_color.setAlpha(self.opacity)
        # collapse_below gradient
        self.collapse_below_gradient = QRadialGradient(-3, -3, 10)
        self.collapse_below_gradient.setColorAt(0, self.c2.lighter(140))
        self.collapse_below_gradient.setColorAt(1, self.c2.darker(140))

        # changing appearance may change node's bounding rectangle
        self.prepareGeometryChange()

    def type(self):
        return Node.Type

    def add_edge(self, edge):
        self.edge_list.append(edge)

    def edges(self):
        return self.edge_list

    # draw inside this rectangle
    def boundingRect(self):
        adjust = 2
        return QRectF(-self.w/2 - adjust, -self.h/2 - adjust,
                      self.w+self.s + adjust, self.h+self.s + adjust)

    # mouse hovers when inside this rectangle
    def shape(self):
        return self.mouse_path

    def paint(self, painter, option, widget):

        # box gradient
        if self.isSelected():
            self.gradient.setColorAt(0, self.c1.lighter(140))
            self.gradient.setColorAt(0.5, self.c2.lighter(140))
            self.gradient.setColorAt(1, self.c3.lighter(140))
        else:
            self.gradient.setColorAt(0, self.c1)
            self.gradient.setColorAt(0.5, self.c2)
            self.gradient.setColorAt(1, self.c3)

        # box shadow
        if self.node_shadow:
            if self.node_type == "T": # SAY message has right tab fold
                painter.setPen(Qt.NoPen)
                painter.setBrush(self.shadow_color)
                painter.drawPolygon(self.right_shadow_say)
            else:
                painter.fillRect(self.right_shadow, self.shadow_color)
            painter.fillRect(self.bottom_shadow, self.shadow_color)

        # box
        painter.setBrush(QBrush(self.gradient))
        if self.node_border:
            painter.setPen(QPen(self.border_color, 0))
        else:
            painter.setPen(QPen(Qt.NoPen))
        if self.node_type == "T": # SAY message has right tab fold
            painter.drawConvexPolygon(self.tbox)
            painter.drawPolyline(self.tbox_inset)
        else:
            painter.drawRect(self.box)

        # menu icon
        painter.setPen(QPen(self.menu_icon_color, 1, cap=Qt.RoundCap))
        mx, my, mw, mh = self.menu_bounds()
        spacing = mh/3
        for i in range(3):
            painter.drawLine(mx, my+i*spacing, mx+mw, my+i*spacing)

        # collapse_below icon
        if self.collapse_below:
            # move painter to center of icon near top-right corner
            painter.save()
            painter.translate(self.w/2 - 7, -self.h/2 + 7)

            # draw circle shadow
            painter.setPen(Qt.NoPen)
            painter.setBrush(self.shadow_color)
            painter.drawEllipse(-5.8, -5.8, 12, 12)

            # draw circle
            painter.setBrush(QBrush(self.collapse_below_gradient))
            painter.setPen(QPen(self.border_color, 0))
            painter.drawEllipse(-6, -6, 12, 12)
            painter.restore()

        # box text
        painter.setPen(QPen(self.annotation_color, 0))
        painter.drawText(self.box,
                         Qt.AlignCenter|Qt.TextWordWrap, self.label)

        # border if selected
        if self.isSelected():
            painter.setPen(QColor("#e60000"))
            painter.setBrush(QBrush(Qt.NoBrush))
            painter.drawRect(self.box)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged:
            for edge in self.edge_list:
                edge.set_appearance()

        return super(Node, self).itemChange(change, value)

    def mousePressEvent(self, event):
        # select all under IN if SHIFT key is down
        if event.modifiers() == Qt.ShiftModifier:
            node_set = at_and_below_in(self)
            for node in node_set:
                node.setSelected(True)

        self.moved = False # may show menu if False
        super(Node, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        self.moved = True # may show menu if False
        super(Node, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):

        # show menu if not moved, in menu icon, and no keyboard modifier
        clicked_icon = False
        if not self.moved and event.modifiers() == Qt.NoModifier:
            x = event.pos().x()
            y = event.pos().y()
            extra_border = 4
            mx, my, mw, mh = self.menu_bounds()
            if x<=mx+mw+2 + extra_border and y <= my+mh + extra_border:
                self.show_menu()
                clicked_icon = True

        # note selection state before running mouse release in parent
        selected_nodes = list()
        for node in self.graph_item.nodes:
            if node.isSelected():
                selected_nodes.append(node)

        # run mouse release in parent
        super(Node, self).mouseReleaseEvent(event)

        # restore selection as needed
        if event.modifiers() == Qt.ShiftModifier or clicked_icon:
            # keep selections by undoing what the parent did
            for node in selected_nodes:
                node.setSelected(True)

    # right-click shows menu
    def contextMenuEvent(self, event):
        if event.reason() == QGraphicsSceneContextMenuEvent.Mouse:
            self.show_menu()

    def menu_bounds(self):
        mx = -self.w/2+2
        my = -self.h/2+3
        mw = 7
        mh = 9
        return (mx, my, mw, mh)

    def show_menu(self):
        menu = NodeMenu()
        menu.show_menu(self.graph_item, self)

