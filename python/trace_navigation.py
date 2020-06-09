from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout, QPushButton
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtGui import QIntValidator, QIcon
from graph_item import GraphItem

class TraceNavigation(QWidget):
    """Container for trace navigation widgets
    """

    def __init__(self, graphs_manager, graph_list_widget):
        super(TraceNavigation, self).__init__()

        self.graphs_manager = graphs_manager
        self.graph_list_widget = graph_list_widget

        # connect
        graphs_manager.signal_graphs_loaded.connect(self.set_min_max)
        graph_list_widget.signal_graph_selection_changed.connect(
                                                    self.set_trace_number)

        hlayout = QHBoxLayout()
        hlayout.setContentsMargins(5, 0, 5, 0)
        self.previous_btn = QPushButton(QIcon("icons/go-previous-6.png"), "")
        self.previous_btn.clicked.connect(self.go_previous)

        self.next_btn = QPushButton(QIcon("icons/go-next-6.png"), "")
        self.next_btn.clicked.connect(self.go_next)

        self.trace_validator = QIntValidator()
        self.trace_value = QLineEdit(self)
        # default to showing 0, no trace
        self.current_trace = 0
        self.trace_min = 0
        self.trace_max = 0
        self.trace_value.setText(str(self.current_trace))
        self.trace_value.setFixedSize(50,20)
        self.trace_value.setMaxLength(5)

        # what to do when the user inputs a trace number
        # self.trace_value.textEdited.connect(self.trace_edited)
        self.trace_value.returnPressed.connect(self.return_pressed)
        self.trace_value.setValidator(self.trace_validator)
        self.trace_label = QLabel("of X")

        hlayout.addWidget(self.previous_btn)
        hlayout.addWidget(self.next_btn)
        hlayout.addWidget(self.trace_value)
        hlayout.addWidget(self.trace_label)
        # now set layout
        self.setLayout(hlayout)
        # default to widgets disabled
        self.setDisabled(True)

    # set validation limits
    @pyqtSlot()
    def set_min_max(self):
        self.trace_max = len(self.graphs_manager.graphs)
        self.trace_min = min(1, self.trace_max)
        self.trace_validator.setRange(self.trace_min, self.trace_max)
        self.trace_label.setText("of %d" % self.trace_max)

    # set current trace number
    @pyqtSlot(GraphItem)
    def set_trace_number(self, graph_item):
        self.current_trace = graph_item.index
        self.trace_value.setText(str(self.current_trace))

    def trace_edited(self, trace_text):
        try:
            trace_num = int(trace_text)
            if ((trace_num >= self.trace_min) and
                (trace_num <= self.trace_max) and
                (trace_num != self.current_trace)):
                # use -1 because traces are displayed starting at 1,
                # but indexed starting at 0
                glw_new = self.graph_list_widget.model.index(trace_num-1)
                self.graph_list_widget.view.setCurrentIndex(glw_new)
        except:
            pass

    def return_pressed(self):
        trace_text = self.trace_value.text()
        try:
            trace_num = int(trace_text)
            if ((trace_num >= self.trace_min) and
                (trace_num <= self.trace_max) and
                (trace_num != self.current_trace)):
                # use -1 because traces are displayed starting at 1,
                # but indexed starting at 0
                glw_new = self.graph_list_widget.model.index(trace_num-1)
                self.graph_list_widget.view.setCurrentIndex(glw_new)
                self.graph_list_widget.view.scrollTo(glw_new)
        except:
            pass

    def go_previous(self):
        glw_current = self.graph_list_widget.view.currentIndex().row()
        if (glw_current > 0):
            glw_new = self.graph_list_widget.model.index(glw_current-1)
            self.graph_list_widget.view.setCurrentIndex(glw_new)
            self.graph_list_widget.view.scrollTo(glw_new)
        else:
            # already at the beginning of the list
            pass

    def go_next(self):
        glw_current = self.graph_list_widget.view.currentIndex().row()
        if (glw_current < (self.trace_max - 1)):
            glw_new = self.graph_list_widget.model.index(glw_current+1)
            self.graph_list_widget.view.setCurrentIndex(glw_new)
            self.graph_list_widget.view.scrollTo(glw_new)
        else:
            # already at the end of the list
            pass

    def setDisabled(self, new_state):
        self.previous_btn.setDisabled(new_state)
        self.next_btn.setDisabled(new_state)
        self.trace_value.setDisabled(new_state)

    def clear(self):
        self.current_trace = 0
        self.trace_value.setText(str(self.current_trace))
        self.set_min_max()

