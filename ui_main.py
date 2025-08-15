# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainxtkBiG.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QGroupBox, QLabel, QMainWindow,
    QPlainTextEdit, QPushButton, QSizePolicy, QStatusBar,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(810, 608)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.DebugScreenGroup = QGroupBox(self.centralwidget)
        self.DebugScreenGroup.setObjectName(u"DebugScreenGroup")
        self.DebugScreenGroup.setGeometry(QRect(10, 10, 381, 101))
        self.DebugLabel = QLabel(self.DebugScreenGroup)
        self.DebugLabel.setObjectName(u"DebugLabel")
        self.DebugLabel.setGeometry(QRect(10, 10, 361, 20))
        self.DebugLabel.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.DebugLabel.setTextFormat(Qt.TextFormat.PlainText)
        self.DebugLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.DebugPicLabel = QLabel(self.DebugScreenGroup)
        self.DebugPicLabel.setObjectName(u"DebugPicLabel")
        self.DebugPicLabel.setGeometry(QRect(10, 29, 361, 41))
        self.DebugPicLabel.setMaximumSize(QSize(361, 41))
        self.DebugPicLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.DebugNoteLabel = QLabel(self.DebugScreenGroup)
        self.DebugNoteLabel.setObjectName(u"DebugNoteLabel")
        self.DebugNoteLabel.setGeometry(QRect(10, 70, 361, 21))
        self.DebugNoteLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.EventHystoryBox = QGroupBox(self.centralwidget)
        self.EventHystoryBox.setObjectName(u"EventHystoryBox")
        self.EventHystoryBox.setGeometry(QRect(399, 9, 391, 571))
        self.EventHistoryTextEdit = QPlainTextEdit(self.EventHystoryBox)
        self.EventHistoryTextEdit.setObjectName(u"EventHistoryTextEdit")
        self.EventHistoryTextEdit.setGeometry(QRect(10, 10, 371, 551))
        self.EventHistoryTextEdit.setReadOnly(True)
        self.ButtonPanel = QGroupBox(self.centralwidget)
        self.ButtonPanel.setObjectName(u"ButtonPanel")
        self.ButtonPanel.setGeometry(QRect(10, 120, 381, 461))
        self.SampleButton = QPushButton(self.ButtonPanel)
        self.SampleButton.setObjectName(u"SampleButton")
        self.SampleButton.setEnabled(False)
        self.SampleButton.setGeometry(QRect(240, 10, 131, 41))
        self.ChangeCoordsButton = QPushButton(self.ButtonPanel)
        self.ChangeCoordsButton.setObjectName(u"ChangeCoordsButton")
        self.ChangeCoordsButton.setEnabled(False)
        self.ChangeCoordsButton.setGeometry(QRect(10, 10, 121, 41))
        self.StartButton = QPushButton(self.ButtonPanel)
        self.StartButton.setObjectName(u"StartButton")
        self.StartButton.setGeometry(QRect(240, 100, 131, 41))
        self.StopButton = QPushButton(self.ButtonPanel)
        self.StopButton.setObjectName(u"StopButton")
        self.StopButton.setEnabled(False)
        self.StopButton.setGeometry(QRect(10, 100, 121, 41))
        self.GoBackButton = QPushButton(self.ButtonPanel)
        self.GoBackButton.setObjectName(u"GoBackButton")
        self.GoBackButton.setEnabled(False)
        self.GoBackButton.setGeometry(QRect(10, 400, 121, 41))
        self.EvemtBoxOnTop = QPushButton(self.ButtonPanel)
        self.EvemtBoxOnTop.setObjectName(u"EvemtBoxOnTop")
        self.EvemtBoxOnTop.setGeometry(QRect(240, 400, 131, 41))
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        self.statusbar.setEnabled(True)
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.StartButton.clicked["bool"].connect(self.StopButton.setDisabled)
        self.StartButton.clicked["bool"].connect(self.StartButton.setEnabled)
        self.StopButton.clicked["bool"].connect(self.StopButton.setEnabled)
        self.StopButton.clicked["bool"].connect(self.StartButton.setDisabled)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.DebugScreenGroup.setTitle("")
        self.DebugLabel.setText(QCoreApplication.translate("MainWindow", u"Debug picture", None))
        self.DebugPicLabel.setText("")
        self.DebugNoteLabel.setText(QCoreApplication.translate("MainWindow", u"Note: picture in debug screen must be like on a sample picture.", None))
        self.EventHystoryBox.setTitle("")
        self.ButtonPanel.setTitle("")
        self.SampleButton.setText(QCoreApplication.translate("MainWindow", u"Sample", None))
        self.ChangeCoordsButton.setText(QCoreApplication.translate("MainWindow", u"Change coords", None))
        self.StartButton.setText(QCoreApplication.translate("MainWindow", u"Start", None))
        self.StopButton.setText(QCoreApplication.translate("MainWindow", u"Stop", None))
        self.GoBackButton.setText(QCoreApplication.translate("MainWindow", u"Go back", None))
        self.EvemtBoxOnTop.setText(QCoreApplication.translate("MainWindow", u"Event box on top", None))
    # retranslateUi

