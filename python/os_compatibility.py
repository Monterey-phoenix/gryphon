# Compensate for differences between OS systems
from platform import system
from PyQt5.QtCore import Qt

# On Mac keyboard, CRTL returns META instead of CTRL, so compensate.
def control_modifier():
    if system() == "Darwin":
        return Qt.MetaModifier
    else:
        return Qt.ControlModifier

