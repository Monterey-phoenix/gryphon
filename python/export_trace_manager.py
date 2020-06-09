import os
from subprocess import Popen, PIPE
#import shutil
import json
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtGui import QFontMetrics
from PyQt5.QtGui import QPixmap
from PyQt5.QtGui import QPainter
from PyQt5.QtGui import QColor, QLinearGradient, QBrush, QRadialGradient, QPen
from PyQt5.QtWidgets import QStyleOptionViewItem
from graph_item import GraphItem
from settings_manager import settings

"""export_trace_manager manages export of trace image files.
"""

# export trace as image file.  Return (status)
def export_trace(trace_filename, graph_item):

    # painting is much like GraphListItemDelegate.paint().
    # also ref GraphMainView.drawBackground().

    if graph_item == None:
        return("Error: graph not available")

    # font height and banner height
    font_height = QFontMetrics(QFont()).height()
    banner_height = int(font_height * 1.5)

    # find the corners of this graph
    bounding_rect = graph_item.bounding_rect()

    # add border padding
    bounding_rect.adjust(0, 0, banner_height*2, banner_height*2)

    # define the bounding rectangle for pixmap for painter to paint in
    pixmap = QPixmap(bounding_rect.width(), bounding_rect.height())
    painter = QPainter(pixmap)

    # fill background
    gradient = QLinearGradient(bounding_rect.topLeft(),
                               bounding_rect.bottomRight())
    c = QColor(settings["graph_background_c"])
    gradient.setColorAt(0, c.lighter(settings["graph_gradient"]))
    gradient.setColorAt(0.5, c)
    gradient.setColorAt(1, c.darker(settings["graph_gradient"]))
    # zz NOTE: painter must go beyond.  Why?  Use this workaround.
    fill_rect = bounding_rect.adjusted(0, 0, 100,100)
    painter.fillRect(fill_rect, QBrush(gradient))

    # paint the graph index
    painter.drawText(5, font_height, "%s" % graph_item.index)

    # paint mark if graph is marked
    if graph_item.mark == "U":
        # no mark
        pass
    else:
        # get color based on mark
        if graph_item.mark == "M":
            c1 = Qt.red
            c2 = Qt.darkRed
        else:
            # mark not recognized
            c1 = Qt.gray
            c2 = Qt.darkGray

        # move painter to center of mark near top-right corner
        painter.save()
        painter.translate(bounding_rect.width() - 12, 12)

        # draw circle shadow
        painter.setPen(Qt.NoPen)
        painter.setBrush(Qt.darkGray)
        painter.drawEllipse(-5, -5, 14, 14)

        # draw circle
        gradient = QRadialGradient(-3, -3, 10)
        gradient.setColorAt(0, c1)
        gradient.setColorAt(1, c2)
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(Qt.black, 0))
        painter.drawEllipse(-7, -7, 14, 14)
        painter.restore()

    # paint graph
    # transform painter below banner and fit nodes and edges
    painter.save()
    painter.translate(banner_height, banner_height)

    # get a default option object.  It is neither a QStyleOptionViewItem
    # nor a QStyleOptionGraphicsItem and we don't use it, but we need something.
    option = QStyleOptionViewItem()

    # paint nodes and edges
    for edge in graph_item.edges:
        edge.paint(painter, option, None)
    for node in graph_item.nodes:
        # translate for this node
        painter.save()
        painter.translate(node.pos())
        node.paint(painter, option, None)
        painter.restore()

    # restore painter state
    painter.restore()

    # export the JSON multigraph project
    painter.end()
    try:
        pixmap.save(trace_filename)
        return ""

    except Exception as e:
        status = "Error exporting trace image file '%s': %s" % (
                                         trace_filename, str(e))
        return (status)

