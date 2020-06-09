# wrapper from https://stackoverflow.com/questions/2398800/linking-a-qtdesigner-ui-file-to-python-pyqt
import webbrowser
from PyQt5.QtCore import QObject # for signal/slot support
from PyQt5.QtCore import pyqtSlot # for signal/slot support
from PyQt5.QtCore import QRegExp
from PyQt5.QtWidgets import QDialog
from PyQt5.QtGui import QRegExpValidator
from about_mp_dialog import Ui_AboutMPDialog

class AboutMPDialogWrapper(QDialog):
    def __init__(self, parent):
        super(AboutMPDialogWrapper, self).__init__(parent)
        self.ui = Ui_AboutMPDialog()
        self.ui.setupUi(self)

        # connect slots
        self.ui.mp_gryphon_tb.clicked.connect(self.open_mp_gryphon)
        self.ui.nps_tb.clicked.connect(self.open_nps)

        # put in text from file
        with open("html/about.html") as f:
            text = f.read()
#        self.ui.about_te.appendHtml(text)
        self.ui.about_tb.setHtml(text)
        self.ui.about_tb.setOpenExternalLinks(True)

    @pyqtSlot()
    def open_mp_gryphon(self):
        webbrowser.open("http://wiki.nps.edu/display/MP")

    @pyqtSlot()
    def open_nps(self):
        webbrowser.open("http://www.nps.edu")

