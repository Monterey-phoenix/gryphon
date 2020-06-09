# wrapper from https://stackoverflow.com/questions/2398800/linking-a-qtdesigner-ui-file-to-python-pyqt
import webbrowser
from PyQt5.QtCore import QObject # for signal/slot support
from PyQt5.QtCore import pyqtSlot # for signal/slot support
from PyQt5.QtCore import QRegExp
from PyQt5.QtWidgets import QDialog
from PyQt5.QtGui import QRegExpValidator
from keyboard_dialog import Ui_KeyboardDialog

class KeyboardDialogWrapper(QDialog):
    def __init__(self, parent):
        super(KeyboardDialogWrapper, self).__init__(parent)
        self.ui = Ui_KeyboardDialog()
        self.ui.setupUi(self)

        # connect slots
        # none

        # put in text from file
        with open("html/keyboard_shortcuts.html") as f:
            text = f.read()
        self.ui.keyboard_tb.setHtml(text)

