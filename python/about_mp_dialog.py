# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'about_mp_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_AboutMPDialog(object):
    def setupUi(self, AboutMPDialog):
        AboutMPDialog.setObjectName("AboutMPDialog")
        AboutMPDialog.resize(852, 273)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(AboutMPDialog.sizePolicy().hasHeightForWidth())
        AboutMPDialog.setSizePolicy(sizePolicy)
        AboutMPDialog.setStyleSheet("background:white; border:0")
        self.horizontalLayout = QtWidgets.QHBoxLayout(AboutMPDialog)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.widget_2 = QtWidgets.QWidget(AboutMPDialog)
        self.widget_2.setMinimumSize(QtCore.QSize(300, 0))
        self.widget_2.setObjectName("widget_2")
        self.widget = QtWidgets.QWidget(self.widget_2)
        self.widget.setGeometry(QtCore.QRect(0, 0, 300, 300))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(117)
        sizePolicy.setVerticalStretch(28)
        sizePolicy.setHeightForWidth(self.widget.sizePolicy().hasHeightForWidth())
        self.widget.setSizePolicy(sizePolicy)
        self.widget.setMinimumSize(QtCore.QSize(300, 300))
        self.widget.setObjectName("widget")
        self.mp_gryphon_tb = QtWidgets.QToolButton(self.widget)
        self.mp_gryphon_tb.setGeometry(QtCore.QRect(10, 10, 251, 151))
        self.mp_gryphon_tb.setFocusPolicy(QtCore.Qt.NoFocus)
        self.mp_gryphon_tb.setStyleSheet("QToolTip{color:black}")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("images/phoenix_logo_color-01nps_cropped.jpg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.mp_gryphon_tb.setIcon(icon)
        self.mp_gryphon_tb.setIconSize(QtCore.QSize(600, 150))
        self.mp_gryphon_tb.setObjectName("mp_gryphon_tb")
        self.nps_tb = QtWidgets.QToolButton(self.widget)
        self.nps_tb.setGeometry(QtCore.QRect(70, 190, 151, 53))
        self.nps_tb.setFocusPolicy(QtCore.Qt.NoFocus)
        self.nps_tb.setStyleSheet("QToolTip{color:black}")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("images/nps_logo_hz.jpg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.nps_tb.setIcon(icon1)
        self.nps_tb.setIconSize(QtCore.QSize(400, 50))
        self.nps_tb.setObjectName("nps_tb")
        self.horizontalLayout.addWidget(self.widget_2)
        self.about_tb = QtWidgets.QTextBrowser(AboutMPDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.about_tb.sizePolicy().hasHeightForWidth())
        self.about_tb.setSizePolicy(sizePolicy)
        self.about_tb.setFocusPolicy(QtCore.Qt.NoFocus)
        self.about_tb.setObjectName("about_tb")
        self.horizontalLayout.addWidget(self.about_tb)

        self.retranslateUi(AboutMPDialog)
        QtCore.QMetaObject.connectSlotsByName(AboutMPDialog)

    def retranslateUi(self, AboutMPDialog):
        _translate = QtCore.QCoreApplication.translate
        AboutMPDialog.setWindowTitle(_translate("AboutMPDialog", "About Montery Phoenix - Gryphon"))
        self.mp_gryphon_tb.setToolTip(_translate("AboutMPDialog", "http://wiki.nps.edu/display/MP"))
        self.mp_gryphon_tb.setText(_translate("AboutMPDialog", "..."))
        self.nps_tb.setToolTip(_translate("AboutMPDialog", "http://www.nps.edu"))
        self.nps_tb.setText(_translate("AboutMPDialog", "..."))
