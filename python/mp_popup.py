from PyQt5.QtWidgets import QMessageBox

"""Simple message box for simple popup warnings.
"""

def mp_popup(parent, message):
    mb = QMessageBox()
    mb.setText(message)
    mb.exec()

