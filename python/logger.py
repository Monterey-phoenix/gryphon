#!/usr/bin/env python3

from PyQt5.QtWidgets import QPlainTextEdit
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtCore import QObject

"""Log to log_pane and possibly also to status bar"""
class Logger():
    def __init__(self, statusbar):
        self.statusbar = statusbar
        self.log_pane = QPlainTextEdit()
        self.log_pane.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.log_pane.setReadOnly(True)

    # log one line and show in statusbar
    def log(self, log_line):
        self.log_pane.appendPlainText(log_line)
        self.statusbar.showMessage(log_line)

    # log title + log lines
    def log_lines(self, log_title, log_lines):
        self.log_pane.appendPlainText(log_title)
        for line in log_lines:
            self.log_pane.appendPlainText(line)

    # clear the log and clear the statusbar
    def clear_log(self):
        self.log_pane.clear()
        self.statusbar.clearMessage()

