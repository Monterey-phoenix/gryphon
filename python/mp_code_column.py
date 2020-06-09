from PyQt5.QtCore import Qt # for Vertical
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QSplitter

class MPCodeColumn(QWidget):
    """Container for MP Code editor and log pane.
    """

    def __init__(self, gui_manager):
        super(MPCodeColumn, self).__init__()

        vlayout = QVBoxLayout()
        vlayout.setContentsMargins(0, 0, 0, 0)
        self.splitter = QSplitter(Qt.Vertical)
        vlayout.addWidget(self.splitter)

        # code editor
        self.splitter.addWidget(gui_manager.mp_code_editor.code_editor)

        # logger
        self.splitter.addWidget(gui_manager.logger.log_pane)

        # now set layout
        self.setLayout(vlayout)

    # set split sizes
    def set_sizes(self, sizes):
        self.splitter.setSizes(sizes)

