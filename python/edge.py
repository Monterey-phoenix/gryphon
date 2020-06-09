# Adapted from https://raw.githubusercontent.com/baoboa/pyqt5/master/examples/graphicsview/elasticnodes.py

from math import sin, cos, tan, atan2, pi
from PyQt5.QtCore import (QLineF, QPointF, QRectF, QSizeF)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import (QBrush, QColor, QLinearGradient, QPainter,
                         QPainterPath, QPen, QPolygonF, QRadialGradient)
from PyQt5.QtGui import QTransform
from PyQt5.QtGui import QPolygonF
from PyQt5.QtGui import QFontMetrics
from PyQt5.QtGui import QFont
from PyQt5.QtGui import QPainterPath
from PyQt5.QtGui import QPainterPathStroker
from PyQt5.QtWidgets import (QGraphicsItem, QGraphicsView, QStyle)
from PyQt5.QtWidgets import QGraphicsSimpleTextItem
from PyQt5.QtWidgets import QMenu
from PyQt5.QtWidgets import QAction
from PyQt5.QtWidgets import QGraphicsSceneContextMenuEvent
from graphics_rect import graphics_rect
from settings_manager import settings

# Qt line style from MP line style name
def _line_style_lookup(name):
    if name == "solid_line":
        return Qt.SolidLine
    elif name == "dash_line":
        return Qt.DashLine
    else:
        print("Invalid line style name '%s'" % name)
        return Qt.SolidLine

# source point is at edge of source node
def _source_point(source_node, line):
    theta = line.angle() * 2 * pi / 360
    on_side = True
    if line.dx() == 0 or abs(line.dy()/line.dx()) > \
                         source_node.h/source_node.w:
        on_side = False

    if on_side:

        # line enters on side
        if theta < 1/2*pi or theta > 3/2*pi:
            dx = source_node.w/2
            dy = -source_node.w/2 * tan(theta)
        else:
            dx = -source_node.w/2
            dy = source_node.w/2 * tan(theta)

    else:
        # line enters on top or bottom
        # dx
        if tan(theta) == 0:
            dx = 0
        else:
            if theta < pi:
                dx = source_node.h/2 / tan(theta)
            else:
                dx = -source_node.h/2 / tan(theta)
        # dy
        if theta < pi:
            dy = -source_node.h/2
        else:
            dy = source_node.h/2

    return QPointF(dx, dy)

# destination point is at edge of destination node
def _dest_point(dest_node, line):
    theta = line.angle() * 2 * pi / 360
    on_side = True
    if line.dx() == 0 or abs(line.dy()/line.dx()) > \
                         dest_node.h/dest_node.w:
        on_side = False

    if on_side:

        # line enters on side
        if theta < 1/2*pi or theta > 3/2*pi:
            dx = dest_node.w/2
            dy = -dest_node.w/2 * tan(theta)
        else:
            dx = -dest_node.w/2
            dy = dest_node.w/2 * tan(theta)

    else:
        # line enters on top or bottom
        # dx
        if tan(theta) == 0:
            dx = 0
        else:
            if theta < pi:
                dx = dest_node.h/2 / tan(theta)
            else:
                dx = -dest_node.h/2 / tan(theta)
        # dy
        if theta < pi:
            dy = -dest_node.h/2
        else:
            dy = dest_node.h/2

    return QPointF(dx, dy)

# Edge
# note: Edge is in charge of managing its EdgeText
#
# class variables:
#     cbp0, cbp1, cbp2, cbp3: Cubic Bezier points from source to dest
#     old_cbp0, old_cbp3
#     color, line_width, style, arrow_size
#     label: Edge text

class Edge(QGraphicsItem):
    Type = QGraphicsItem.UserType + 2

    def __init__(self, source_id, relation, target_id, label, node_lookup,
                 cbp1 = None, cbp2 = None):
        super(Edge, self).__init__()

        # MP attributes
        self.source_id = source_id
        self.relation = relation
        self.target_id = target_id
        self.label = label
        self.node_lookup = node_lookup
        self.cbp1 = cbp1 # cubic bezier point 1 QPointF
        self.cbp2 = cbp2

    def type(self):
        return Edge.Type

    # optimization: just-in-time for display, see graph_item.py.
    # Also call set_appearance().
    def initialize_edge(self, placer):

        # graphicsItem mode
        self.setFlag(QGraphicsItem.ItemIsSelectable)

        self.source_node = self.node_lookup[self.source_id]
        self.dest_node = self.node_lookup[self.target_id]
        self.source_node.add_edge(self)
        self.dest_node.add_edge(self)

        # old points to manage move
        self.old_cbp0 = self.mapFromItem(self.source_node, 0, 0)
        self.old_cbp3 = self.mapFromItem(self.dest_node, 0, 0)

        # manually place Cubic Bezier points if not established yet
        if not self.cbp1:
            placer.place_cubic_bezier_points(self)

        # state
        self.show_grips = False

    # move grips and usually update old_cbp0 and old_cbp3 to new positions
    def _move_grips(self):

        # endpoints are same node
        if self.source_node == self.dest_node:
            delta = self.cbp0 - self.old_cbp0
            self.cbp1 += delta
            self.cbp2 += delta

            # move old endpoints to new position
            self.old_cbp0 = self.cbp0
            return

        # old line angle and length
        l = QLineF(self.old_cbp0, self.old_cbp3)
        old_angle = l.angle()
        old_length = l.length()

        # new line angle and length
        l = QLineF(self.cbp0, self.cbp3)
        new_angle = l.angle()
        new_length = l.length()

        # too close to matter and can cause /0 error
        if new_length < 1:
            return

        # establish values if old endpoints were the same
        if old_length == 0:
            # manually separate Cubic Bezier points since not established yet
            self.cbp1 = (2*self.cbp0 + self.cbp3)/3 # 1/3 across
            self.cbp2 = (self.cbp0 + 2*self.cbp3)/3 # 2/3 across

            # move old endpoints to new position
            self.old_cbp0 = self.cbp0
            self.old_cbp3 = self.cbp3
            return

        # scale and delta angle to calculate new grip positions
        scale = new_length / old_length
        angle = new_angle - old_angle

        # p1 angle and length with respect to old_cbp0
        l1 = QLineF(self.old_cbp0, self.cbp1)
        l1_angle = l1.angle()
        l1_length = l1.length()

        # new l1 starting at cbp0 with scaled length and adjusted angle
        new_l1 = QLineF(self.cbp0, self.cbp0 + QPointF(l1_length * scale, 0))
        new_l1.setAngle(l1_angle + angle)

        # new p1
        self.cbp1 = new_l1.p2()

        # p2 angle and length with respect to old_cbp0
        l2 = QLineF(self.old_cbp0, self.cbp2)
        l2_angle = l2.angle()
        l2_length = l2.length()

        # new l2 starting at cbp0 with scaled length and adjusted angle
        new_l2 = QLineF(self.cbp0, self.cbp0 + QPointF(l2_length * scale, 0))
        new_l2.setAngle(l2_angle + angle)

        # new p2
        self.cbp2 = new_l2.p2()

        # move old endpoints to new position
        self.old_cbp0 = self.cbp0
        self.old_cbp3 = self.cbp3

    # adjust for appearance change or for node position change
    def set_appearance(self):

        # Cubic Bezier path
        self.cbp0 = self.mapFromItem(self.source_node, 0, 0)
        self.cbp3 = self.mapFromItem(self.dest_node, 0, 0)
        if self.old_cbp0 != self.cbp0 or self.old_cbp3 != self.cbp3:
            self._move_grips()
        self.edge_path = QPainterPath(self.cbp0)
        self.edge_path.cubicTo(self.cbp1, self.cbp2, self.cbp3)

        # the path region for mouse detection
        # note: path without stroker includes concave shape, not just edge path
        painter_path_stroker = QPainterPathStroker()
        self.mouse_path = painter_path_stroker.createStroke(self.edge_path)

        # get coordinate of arrow tip based on destination node
        # using binary search
        edge_path = self.edge_path
        dest_path = self.mapFromItem(self.dest_node, self.dest_node.mouse_path)
        t = 0.5
        m = 0.25
        for i in range(10): # binary search edge with resolution of 12
            arrow_tip = edge_path.pointAtPercent(t)
            if dest_path.contains(arrow_tip):
                # inside dest so move back
                t -= m
            else:
                # outside dest so move toward
                t += m
            m /= 2

        # define the arrow shape as a polygon
        arrow_size = settings["edge_arrow_size"]
        # angleAtPercent takes way too much time so calculate directly instead,
        # https://stackoverflow.com/questions/4089443/find-the-tangent-of-a-point-on-a-cubic-bezier-curve
        omt = 1 - t # one minus t
        arrow_tangent_point = 3*omt*omt*(self.cbp1 - self.cbp2) + \
                              6*t*omt*(self.cbp2 - self.cbp1) + \
                              3*t*t*(self.cbp3 - self.cbp2)
        theta = atan2(-arrow_tangent_point.y(), arrow_tangent_point.x())
        dest_p1 = arrow_tip + QPointF(
                   sin(theta - pi / 3) * arrow_size,
                   cos(theta - pi / 3) * arrow_size)
        dest_p2 = arrow_tip + QPointF(
                   sin(theta - pi + pi / 3) * arrow_size,
                   cos(theta - pi + pi / 3) * arrow_size)
        self.arrow = QPolygonF([arrow_tip, dest_p1, dest_p2])

        # line color based on line relation
        self.line_width = 1
        if self.relation == "IN":
            self.color = QColor(settings["edge_in_c"])
            self.style = _line_style_lookup(settings["edge_in_style"])
        elif self.relation == "FOLLOWS":
            self.color = QColor(settings["edge_follows_c"])
            self.style = _line_style_lookup(settings["edge_follows_style"])
        elif self.relation == "COLLAPSED_FOLLOWS":
            self.color = QColor("#000000")
            self.style = Qt.SolidLine
            self.line_width = 2
        elif self.relation == "USER_DEFINED":
            self.color = QColor(settings["edge_user_defined_c"])
            self.style = _line_style_lookup(settings["edge_user_defined_style"])
        else:
            print("unrecognized edge relation '%s'" % self.relation)
            self.color = QColor(Qt.gray)
            self.style = Qt.SolidLine

        # define edge text point if edge text is present
        if self.label:
            self.label_point = edge_path.pointAtPercent(0.5)

        # Use opacity if node on either side is hidden or collapsed
        if self.source_node.hide or self.source_node.collapse or \
                      self.dest_node.hide or self.dest_node.collapse:
            self.color.setAlpha(settings["graph_hide_collapse_opacity"])

        # use opaque red instead if showing grips
        if self.show_grips:
            self.color = QColor(Qt.red)

        # about to change line's bounding rectangle
        self.prepareGeometryChange()

    def boundingRect(self):
        extra = 1
        return self.edge_path.boundingRect().adjusted(-extra, -extra,
                                                            extra, extra)

    def shape(self):
        # note: path without stroker includes concave shape, not just edge path
        return self.mouse_path

    def paint(self, painter, option, widget):

        # paint edge shape of path without brush fill
        painter.strokePath(self.edge_path, QPen(self.color, self.line_width,
                                   self.style, Qt.RoundCap, Qt.RoundJoin))

        # draw the arrow
        painter.setPen(QPen(self.color, self.line_width, self.style,                                           Qt.RoundCap, Qt.RoundJoin))
        painter.setBrush(self.color)
        painter.drawPolygon(self.arrow)

        # draw edge label if present
        if self.label:
            fm = painter.fontMetrics()
            label_width = fm.width(self.label)
            label_descent = fm.descent()
            offset = QPointF(label_width/2, label_descent+1)
            painter.drawText(self.label_point - offset, self.label)

    # paint using p0, p1, p2, p3, color, line_width, style
    def draw_cubic_bezier(self):
        painter.setPen(QPen(self.color, self.line_width, self.style,
                                          Qt.RoundCap, Qt.RoundJoin))
        painter.moveTo(self.p0)
        painter.cubicTo(self.p1, self.p2, self.p3)

    def mousePressEvent(self, event):
        # deselect any nodes
        for node in self.source_node.graph_item.nodes:
            node.setSelected(False)

        # show grips
        self.scene().show_grips(self)

