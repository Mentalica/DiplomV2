# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui\RegisterPage.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setMinimumSize(QtCore.QSize(800, 600))
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(0, 0, 800, 600))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setSpacing(3)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setSpacing(3)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.RegisterFrame = QtWidgets.QFrame(self.horizontalLayoutWidget)
        self.RegisterFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.RegisterFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.RegisterFrame.setObjectName("RegisterFrame")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.RegisterFrame)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_4.addItem(spacerItem1)
        self.LoginLabel = QtWidgets.QFrame(self.RegisterFrame)
        self.LoginLabel.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.LoginLabel.setFrameShadow(QtWidgets.QFrame.Raised)
        self.LoginLabel.setObjectName("LoginLabel")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.LoginLabel)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.RegisterStatus = QtWidgets.QLabel(self.LoginLabel)
        font = QtGui.QFont()
        font.setPointSize(13)
        self.RegisterStatus.setFont(font)
        self.RegisterStatus.setObjectName("RegisterStatus")
        self.verticalLayout_2.addWidget(self.RegisterStatus)
        self.verticalLayout_4.addWidget(self.LoginLabel)
        self.InpuxBoxes = QtWidgets.QFrame(self.RegisterFrame)
        self.InpuxBoxes.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.InpuxBoxes.setFrameShadow(QtWidgets.QFrame.Raised)
        self.InpuxBoxes.setObjectName("InpuxBoxes")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.InpuxBoxes)
        self.verticalLayout.setObjectName("verticalLayout")
        self.email_text = QtWidgets.QLabel(self.InpuxBoxes)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.email_text.setFont(font)
        self.email_text.setObjectName("email_text")
        self.verticalLayout.addWidget(self.email_text)
        self.email_input = QtWidgets.QLineEdit(self.InpuxBoxes)
        self.email_input.setMinimumSize(QtCore.QSize(0, 25))
        self.email_input.setInputMethodHints(QtCore.Qt.ImhNone)
        self.email_input.setPlaceholderText("")
        self.email_input.setObjectName("email_input")
        self.verticalLayout.addWidget(self.email_input)
        self.password_text = QtWidgets.QLabel(self.InpuxBoxes)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.password_text.setFont(font)
        self.password_text.setObjectName("password_text")
        self.verticalLayout.addWidget(self.password_text)
        self.password_input = QtWidgets.QLineEdit(self.InpuxBoxes)
        self.password_input.setMinimumSize(QtCore.QSize(0, 25))
        self.password_input.setInputMethodHints(QtCore.Qt.ImhHiddenText|QtCore.Qt.ImhNoAutoUppercase|QtCore.Qt.ImhNoPredictiveText|QtCore.Qt.ImhSensitiveData)
        self.password_input.setFrame(True)
        self.password_input.setEchoMode(QtWidgets.QLineEdit.Password)
        self.password_input.setPlaceholderText("")
        self.password_input.setObjectName("password_input")
        self.verticalLayout.addWidget(self.password_input)
        self.username_text = QtWidgets.QLabel(self.InpuxBoxes)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.username_text.setFont(font)
        self.username_text.setObjectName("username_text")
        self.verticalLayout.addWidget(self.username_text)
        self.username_input = QtWidgets.QLineEdit(self.InpuxBoxes)
        self.username_input.setMinimumSize(QtCore.QSize(0, 25))
        self.username_input.setInputMethodHints(QtCore.Qt.ImhNone)
        self.username_input.setFrame(True)
        self.username_input.setEchoMode(QtWidgets.QLineEdit.Normal)
        self.username_input.setPlaceholderText("")
        self.username_input.setObjectName("username_input")
        self.verticalLayout.addWidget(self.username_input)
        self.verticalLayout_4.addWidget(self.InpuxBoxes)
        self.PushButtons = QtWidgets.QFrame(self.RegisterFrame)
        self.PushButtons.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.PushButtons.setFrameShadow(QtWidgets.QFrame.Raised)
        self.PushButtons.setObjectName("PushButtons")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.PushButtons)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.confirm_button = QtWidgets.QPushButton(self.PushButtons)
        self.confirm_button.setObjectName("confirm_button")
        self.horizontalLayout.addWidget(self.confirm_button)
        self.login_button = QtWidgets.QPushButton(self.PushButtons)
        self.login_button.setObjectName("login_button")
        self.horizontalLayout.addWidget(self.login_button)
        self.verticalLayout_4.addWidget(self.PushButtons)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_4.addItem(spacerItem2)
        self.verticalLayout_3.addWidget(self.RegisterFrame)
        self.horizontalLayout_2.addLayout(self.verticalLayout_3)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem3)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 897, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.RegisterStatus.setText(_translate("MainWindow", "Sign Up"))
        self.email_text.setText(_translate("MainWindow", "Email"))
        self.password_text.setText(_translate("MainWindow", "Password"))
        self.username_text.setText(_translate("MainWindow", "Username"))
        self.confirm_button.setText(_translate("MainWindow", "Confirm"))
        self.login_button.setText(_translate("MainWindow", "Login"))
