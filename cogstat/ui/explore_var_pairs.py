# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'explore_var_pairs.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(400, 280)
        Dialog.setMinimumSize(QtCore.QSize(400, 280))
        Dialog.setMaximumSize(QtCore.QSize(400, 280))
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setEnabled(True)
        self.buttonBox.setGeometry(QtCore.QRect(190, 240, 201, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(False)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.source_listWidget = QtGui.QListWidget(Dialog)
        self.source_listWidget.setGeometry(QtCore.QRect(20, 30, 161, 192))
        self.source_listWidget.setMouseTracking(False)
        self.source_listWidget.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.source_listWidget.setObjectName(_fromUtf8("source_listWidget"))
        self.selected_listWidget = QtGui.QListWidget(Dialog)
        self.selected_listWidget.setEnabled(True)
        self.selected_listWidget.setGeometry(QtCore.QRect(220, 30, 171, 192))
        self.selected_listWidget.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.selected_listWidget.setObjectName(_fromUtf8("selected_listWidget"))
        self.label = QtGui.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(20, 10, 151, 16))
        self.label.setObjectName(_fromUtf8("label"))
        self.label_2 = QtGui.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(220, 10, 121, 16))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.addVar = QtGui.QPushButton(Dialog)
        self.addVar.setGeometry(QtCore.QRect(190, 90, 21, 21))
        self.addVar.setObjectName(_fromUtf8("addVar"))
        self.removeVar = QtGui.QPushButton(Dialog)
        self.removeVar.setGeometry(QtCore.QRect(190, 120, 21, 21))
        self.removeVar.setObjectName(_fromUtf8("removeVar"))

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Explore relation of variable pairs", None))
        self.label.setText(_translate("Dialog", "Available variables", None))
        self.label_2.setText(_translate("Dialog", "Selected variables", None))
        self.addVar.setText(_translate("Dialog", "=>", None))
        self.removeVar.setText(_translate("Dialog", "<=", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

