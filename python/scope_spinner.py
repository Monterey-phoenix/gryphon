from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QSpinBox
from PyQt5.QtWidgets import QSizePolicy

"""ScopeSpinner provides spinner and scope accessors.
"""

class ScopeSpinner():

    def __init__(self):
        self.spinner = QSpinBox()
        self.spinner.setRange(1,5)
        self.spinner.setStatusTip("set scope for MP Code run")
        self.spinner.setToolTip("scope")
        self.spinner.setSizePolicy(QSizePolicy.Maximum,
                                         QSizePolicy.Maximum)

    def scope(self):
        return self.spinner.value()

    def set_scope(self, scope):
        self.spinner.setValue(scope)

    def reset(self):
        self.spinner.setValue(1)

