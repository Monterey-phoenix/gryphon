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
from settings_manager import settings

# EdgeGrip
class EdgeGrip(QGraphicsItem):
    Type = QGraphicsItem.UserType + 3

    def __init__(self, grip_side):
        super(EdgeGrip, self).__init__()

        # active side, "source" or "dest"
        self.grip_side = grip_side

        # graphicsItem mode
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setZValue(3)
        self.setVisible(False)

        # bounding rectangle and shape
        d = 14 # diameter
        a = 2 # border adjust
        s = 1 # shadow
        self.bounding_rectangle = QRectF(-d/2-a, -d/2-a, d+s+a, d+s+a)
        self.grip_shape = QPainterPath()
        self.grip_shape.addEllipse(QPointF(0, 0), d/2, d/2)
        self.grip_shadow = QPainterPath()
        self.grip_shadow.addEllipse(QPointF(s,s), d/2, d/2)

        # gradient
        self.gradient = QRadialGradient(-2, -2, 0.7*d)

        # edge
        self.edge = None

    def show_grip(self, edge):
        # bind edge to grip
        self.edge = edge

        # bind properties to grip depending on source or dest side
        if self.grip_side == "source":
            self.setPos(edge.cbp1)
            self.color = QColor(settings["node_root_c"]) # use root color
        elif self.grip_side == "dest":
            self.setPos(edge.cbp2)
            self.color = QColor(settings["node_atomic_c"]) # use atomic color
        else:
            raise Exception("Bad")
        self.setVisible(True)

    def clear_grip(self):
        self.setVisible(False)
    
    def type(self):
        return EdgeGrip.Type

    # draw inside this rectangle
    def boundingRect(self):
        return self.bounding_rectangle

    # mouse considered hovering when inside this rectangle
    def shape(self):
        return self.grip_shape

    def paint(self, painter, option, widget):

            # draw circle shadow
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(Qt.darkGray))
            painter.drawPath(self.grip_shadow)

            # circle gradient color
            if self.isSelected():
                self.gradient.setColorAt(0, self.color.lighter(170))
                self.gradient.setColorAt(1, self.color.darker(110))
            else:
                self.gradient.setColorAt(0, self.color.lighter(140))
                self.gradient.setColorAt(1, self.color.darker(140))

            # draw circle
            painter.setBrush(QBrush(self.gradient))
            painter.setPen(QPen(QColor(Qt.red), 0))
            painter.drawPath(self.grip_shape)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged:
            if self.grip_side == "source":
                self.edge.cbp1 = self.pos()
            elif self.grip_side == "dest":
                self.edge.cbp2 = self.pos()
            else:
                raise Exception("Bad")
            self.edge.set_appearance()

        return super(EdgeGrip, self).itemChange(change, value)

