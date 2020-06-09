# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'keyboard_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_KeyboardDialog(object):
    def setupUi(self, KeyboardDialog):
        KeyboardDialog.setObjectName("KeyboardDialog")
        KeyboardDialog.resize(512, 673)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(KeyboardDialog.sizePolicy().hasHeightForWidth())
        KeyboardDialog.setSizePolicy(sizePolicy)
        KeyboardDialog.setStyleSheet("background:white; border:0")
        self.horizontalLayout = QtWidgets.QHBoxLayout(KeyboardDialog)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.keyboard_tb = QtWidgets.QTextBrowser(KeyboardDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.keyboard_tb.sizePolicy().hasHeightForWidth())
        self.keyboard_tb.setSizePolicy(sizePolicy)
        self.keyboard_tb.setFocusPolicy(QtCore.Qt.NoFocus)
        self.keyboard_tb.setObjectName("keyboard_tb")
        self.horizontalLayout.addWidget(self.keyboard_tb)

        self.retranslateUi(KeyboardDialog)
        QtCore.QMetaObject.connectSlotsByName(KeyboardDialog)

    def retranslateUi(self, KeyboardDialog):
        _translate = QtCore.QCoreApplication.translate
        KeyboardDialog.setWindowTitle(_translate("KeyboardDialog", "Monterey Phoenix - Gryphon Keyboard Shortcuts"))

