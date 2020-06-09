#from PyQt5.QtCore import QObject # for signal/slot support
#from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QColorDialog
from PyQt5.QtGui import QColor
from mp_popup import mp_popup
from settings_manager import settings

class ColorSelectorWidget:

    def __init__(self, parent, settings_manager, key):
        super(ColorSelectorWidget, self).__init__()

        self.settings_manager = settings_manager
        self.key = key

        # QColor color
        color = QColorDialog.getColor(QColor(settings[key]),
                                      parent,
                                      "Select Color for %s" % key,
                                      QColorDialog.DontUseNativeDialog)

        if color.isValid():
            self.settings_manager.change({key:color.name()})

