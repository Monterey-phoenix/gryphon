from PyQt5.QtCore import QObject # for signal/slot support

from PyQt5.QtGui import QColor
from PyQt5.QtGui import QRadialGradient
from PyQt5.QtGui import QBrush
from PyQt5.QtGui import QPen
from PyQt5.QtGui import QTransform
from PyQt5.QtGui import QFontMetrics
from PyQt5.QtGui import QFont
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QRectF, QRect
from PyQt5.QtCore import QAbstractListModel
from PyQt5.QtCore import QSortFilterProxyModel
from PyQt5.QtCore import QVariant
#from PyQt5.QtCore import QModelIndex
from PyQt5.QtCore import QSize

from PyQt5.QtWidgets import QListView
from PyQt5.QtWidgets import QStyledItemDelegate
from PyQt5.QtWidgets import QListWidgetItem
from PyQt5.QtWidgets import QStyle

from graph_item import GraphItem
from graphics_rect import graphics_rect

"""GraphListWidget provides the graph list.  It wraps details of parts,
ref. http://doc.qt.io/qt-5/model-view-programming.html.

Parts:
  * GraphListModel         Provides graphs from graph_manager
zz FUTURE  * GraphProxyModel        Sits between model and view to provide sort and
                           filter functions
  * GraphListView          Manages view
  * GraphListItemDelegate  Provides the paint function for each graph list item

Signals:
  * signal_graph_selection_changed(GraphItem)
"""

# GraphListModel
"""Links the QAbstractListModel to the graph_manager's list subscript.
Listens to graphs_manager graph changed event to replace the data."""
# ref. https://stackoverflow.com/questions/17231184/insert-and-remove-items-from-a-qabstractlistmodel
class GraphListModel(QAbstractListModel):

    def __init__(self, graphs_manager):
        super(GraphListModel, self).__init__()

        # the graphs manager
        self.graphs_manager = graphs_manager

        # connect
        graphs_manager.signal_graphs_loaded.connect(self.reset_list)

    # number of rows
    def rowCount(self, _parent):
        return len(self.graphs_manager.graphs)

    # graph subscript
    def data(self, model_index, role=Qt.DisplayRole):
        if model_index.isValid():
            if role == Qt.DisplayRole:
                return QVariant(model_index.row())
        return QVariant()

    # reset list
    @pyqtSlot()
    def reset_list(self):
        self.beginResetModel()
        self.endResetModel()

# GraphListView
class GraphListView(QListView):

    def __init__(self, parent, graph_list_widget, graph_list_width_manager):
        super(GraphListView, self).__init__(parent)
        self.graph_list_widget = graph_list_widget

        self.setResizeMode(QListView.Adjust)

        graph_list_width_manager.signal_graph_list_width_changed.connect(
                                                         self.changed_width)

    # user selection changed
    def currentChanged(self, current, previous):
        self.graph_list_widget.selection_changed(current.row())

    # width changed
    @pyqtSlot(int)
    def changed_width(self, width):
        # no: self.update()
        # hack from https://stackoverflow.com/questions/16444558/how-to-force-qabstractitemview-recalculate-items-sizehints
        hack_size = self.viewport().size()
        hack_size.setHeight(hack_size.height()+1)
        self.viewport().resize(hack_size)
        hack_size.setHeight(hack_size.height()-1)
        self.viewport().resize(hack_size)

# GraphListItemDelegate
# ref. https://github.com/scopchanov/CustomList/blob/master/app/src/Delegate.cpp
class GraphListItemDelegate(QStyledItemDelegate):

    def __init__(self, graphs_manager, graph_list_width_manager):
        super(GraphListItemDelegate, self).__init__()
        self.graphs_manager = graphs_manager
        self.graph_list_width_manager = graph_list_width_manager

        # font height and banner height
        self.font_height = QFontMetrics(QFont()).height()
        self.banner_height = int(self.font_height * 1.5)

   # paint
    def paint(self, painter, option, model_index):
        painter.save()
        painter.setClipping(True)
        painter.setClipRect(option.rect)

        selected = option.state & QStyle.State_Selected
        hovered = option.state & QStyle.State_MouseOver

        # this graph
        graph_item = self.graphs_manager.graphs[model_index.row()]

        # find the corners of this graph
        graph_bounds = graph_item.bounding_rect()

        # find the larger size to fit this graph in a square
        if graph_bounds.height() > graph_bounds.width():
            size = graph_bounds.height()
        else:
            size = graph_bounds.width()

        # avoid division by zero
        if size == 0:
            size = 1

        # find the scaling factor to fit this graph into the list width
        scale = (self.graph_list_width_manager.width -
                 self.graph_list_width_manager.scrollbar_width) / size

        # paint background
        if selected:
            if hovered:
                background_color = QColor(Qt.blue).lighter(197)
            else:
                background_color = QColor(Qt.blue).lighter(200)
        else:
            if hovered:
                background_color = QColor(Qt.blue).lighter(188)
            else:
                background_color = QColor(Qt.blue).lighter(192)

        painter.fillRect(option.rect.adjusted(0,0,0,-1), background_color)

        # translate axis to cell
        painter.translate(option.rect.x(), option.rect.y())

        # paint the graph index
        painter.drawText(5, self.font_height, "%s  p=%.8g" % (graph_item.index,
                                                     graph_item.probability))

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
            painter.translate(option.rect.width() - 12, 12)

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
        painter.translate(0, self.banner_height)
        painter.scale(scale, scale)
        painter.translate(-graph_bounds.x(), -graph_bounds.y())

        # paint nodes and edges
        for edge in graph_item.edges:
            edge.paint(painter, option, self.parent)
        for node in graph_item.nodes:
            # translate for this node
            painter.save()
            painter.translate(node.pos())
            node.paint(painter, option, self.parent)
            painter.restore()

        # done rescale painter to fit nodes and edges
        painter.restore()

        # draw dividing line
        painter.setPen(Qt.gray)
        bottom = option.rect.height() - 1
        width = option.rect.width()
        painter.drawLine(0, bottom, width, bottom)

        # restore painter state
        painter.restore()

    # sizeHint
    def sizeHint(self, option, model_index):
        # Make width hint narrow to prevent horizontal scrollbar.
        # Use a small width hint.  It needs to be smaller than list width
        # minus scrollbar width minus widget padding, which might be four.
        # Make 1 taller for dividing line so actual graph is square.
        # The size actually provided to paint() is in option.rect.
        return QSize(1, self.graph_list_width_manager.width -
                        self.graph_list_width_manager.scrollbar_width + 1 +
                        self.banner_height)

# zz FUTURE
## GraphProxyModel
## Implement lessThan(), then call sort() to sort the graph list as desired
#class GraphProxyModel(QSortFilterProxyModel):
#
#    def __init__(self, graphs_manager):
#        super(GraphProxyModel, self).__init__()
#        self.graphs_manager = graphs_manager
#
#        # set sort_mode for lessThan.  Add possibilities as desired:
#        # "index" - graph index
#        # "mark" - graph mark, currently "U" or "M"
#        self.sort_mode = "index"
#
#    # set sort mode and sort
#    def sort_by_mode(self, mode):
#        self.sort_mode = mode
#        self.invalidate()
#        self.sort(0) # list so sort column 0
#
#    def lessThan(self, left, right): # QModelIndex
#        print("lessThan %s %d %d" % (self.sort_mode, 
#            self.graphs_manager.graphs[left.row()].index,
#                   self.graphs_manager.graphs[right.row()].index))
#
#
#
#        if self.sort_mode == "index":
#            return self.graphs_manager.graphs[left.row()].index < \
#                   self.graphs_manager.graphs[right.row()].index
#        elif self.sort_mode == "mark":
#            return self.graphs_manager.graphs[left.row()].mark < \
#                   self.graphs_manager.graphs[right.row()].mark
#        else:
#            # undefined mode
#            print("program error: undefined mode %s in GraphProxyModel" %
#                                                                  self.mode)
#            return self.graphs_manager.graphs[left.row()].index < \
#                   self.graphs_manager.graphs[right.row()].index

class GraphListWidget(QObject):

    # signals
    signal_graph_selection_changed = pyqtSignal(GraphItem,
                                        name='graphSelectionChanged')

    def __init__(self, main_splitter, graphs_manager, graph_list_width_manager):
        super(GraphListWidget, self).__init__()
        self.graphs_manager = graphs_manager

        # assemble the components that make up the GraphListWidget service
        self.model = GraphListModel(graphs_manager)
        self.view = GraphListView(main_splitter, self, graph_list_width_manager)
        self.view.setModel(self.model)
        self.delegate = GraphListItemDelegate(graphs_manager,
                                              graph_list_width_manager)
        self.view.setItemDelegate(self.delegate)

        # connect to repaint view when graph appearance changes
        graphs_manager.signal_appearance_changed.connect(self.view.update)

    # view calls this when the user selection changed
    def selection_changed(self, graph_subscript):
        if (graph_subscript == -1):
            # nothing selected
            return

        self.signal_graph_selection_changed.emit(
                               self.graphs_manager.graphs[graph_subscript])

    # select row containing graph, this signals change, returns bool
    def select_graph(self, graph):
        if graph:
            list_model_index = self.model.index(
                                self.graphs_manager.graphs.index(graph))
            self.view.setCurrentIndex(list_model_index)
            return True
        else:
            return False

    # get the graph that is selected in the model else None
    def selected_graph(self):
        graph_subscript = self.view.currentIndex().row()
        if graph_subscript == -1:
            return None
        else:
            # graph_index associated with the selected data model index
            return self.graphs_manager.graphs[graph_subscript]

    # signal this to signal when the graph item needs repainted in the list
    @pyqtSlot(GraphItem)
    def graph_item_view_changed(self, graph_item):
        graph_subscript = self.graphs_manager.graphs.index(graph_item)
        list_model_index = self.model.index(graph_subscript)
        self.model.dataChanged.emit(list_model_index, list_model_index)

# zz Future
#    # sort the list per requested sort mode
#    def sort_list(self, sort_mode):
#        self.proxy_model.sort_by_mode(sort_mode)

