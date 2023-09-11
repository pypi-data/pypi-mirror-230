from PyQt5 import QtCore, QtGui, QtWidgets
import easygui
import sys


# 示例:python -m PyQt5.uic.pyuic temp.ui -o temp_ui.py
# 由qt生成
class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(747, 543)
        self.plainTextEdit = QtWidgets.QPlainTextEdit(Dialog)
        self.plainTextEdit.setGeometry(QtCore.QRect(30, 290, 691, 231))
        self.plainTextEdit.setObjectName("plainTextEdit")
        self.groupBox = QtWidgets.QGroupBox(Dialog)
        self.groupBox.setGeometry(QtCore.QRect(30, 30, 691, 111))
        self.groupBox.setObjectName("groupBox")
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setGeometry(QtCore.QRect(20, 20, 651, 16))
        self.label.setObjectName("label")
        self.pushButton = QtWidgets.QPushButton(self.groupBox)
        self.pushButton.setGeometry(QtCore.QRect(190, 70, 75, 23))
        self.pushButton.setObjectName("pushButton")
        self.pushButton_2 = QtWidgets.QPushButton(self.groupBox)
        self.pushButton_2.setGeometry(QtCore.QRect(420, 70, 75, 23))
        self.pushButton_2.setObjectName("pushButton_2")
        self.groupBox_2 = QtWidgets.QGroupBox(Dialog)
        self.groupBox_2.setGeometry(QtCore.QRect(30, 170, 691, 111))
        self.groupBox_2.setObjectName("groupBox_2")
        self.lineEdit = QtWidgets.QLineEdit(self.groupBox_2)
        self.lineEdit.setGeometry(QtCore.QRect(50, 30, 113, 20))
        self.lineEdit.setObjectName("lineEdit")
        self.lineEdit_2 = QtWidgets.QLineEdit(self.groupBox_2)
        self.lineEdit_2.setGeometry(QtCore.QRect(220, 30, 113, 20))
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.lineEdit_3 = QtWidgets.QLineEdit(self.groupBox_2)
        self.lineEdit_3.setGeometry(QtCore.QRect(400, 30, 113, 20))
        self.lineEdit_3.setObjectName("lineEdit_3")
        self.label_2 = QtWidgets.QLabel(self.groupBox_2)
        self.label_2.setGeometry(QtCore.QRect(20, 30, 31, 16))
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(self.groupBox_2)
        self.label_3.setGeometry(QtCore.QRect(180, 30, 54, 12))
        self.label_3.setObjectName("label_3")
        self.label_4 = QtWidgets.QLabel(self.groupBox_2)
        self.label_4.setGeometry(QtCore.QRect(350, 30, 54, 12))
        self.label_4.setObjectName("label_4")
        self.pushButton_3 = QtWidgets.QPushButton(self.groupBox_2)
        self.pushButton_3.setGeometry(QtCore.QRect(550, 30, 75, 23))
        self.pushButton_3.setMouseTracking(False)
        self.pushButton_3.setObjectName("pushButton_3")
        self.pushButton_4 = QtWidgets.QPushButton(self.groupBox_2)
        self.pushButton_4.setGeometry(QtCore.QRect(310, 70, 75, 23))
        self.pushButton_4.setObjectName("pushButton_4")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.groupBox.setTitle(_translate("Dialog", "上传数据:"))
        self.label.setText(_translate("Dialog", "文件路径"))
        self.pushButton.setText(_translate("Dialog", "选择文件"))
        self.pushButton_2.setText(_translate("Dialog", "执行"))
        self.groupBox_2.setTitle(_translate("Dialog", "删除适配:"))
        self.label_2.setText(_translate("Dialog", "year"))
        self.label_3.setText(_translate("Dialog", "make"))
        self.label_4.setText(_translate("Dialog", "model"))
        self.pushButton_3.setText(_translate("Dialog", "删除单条"))
        self.pushButton_4.setText(_translate("Dialog", "删除全部"))


# 执行类
class MyWindow(QtWidgets.QWidget, Ui_Dialog):  # 括号中的Ui_Form要跟ui.py文件里的class同名
    def __init__(self, parent=None):
        super(MyWindow, self).__init__(parent)
        self.setupUi(self)  # 生成界面
        QtWidgets.QApplication.setStyle(QtWidgets.QStyleFactory.create('Fusion'))  # 界面风格
        # 赋予动作事件
        self.pushButton.clicked.connect(self.select)  # 按钮信号槽
        self.pushButton_2.clicked.connect(self.run)  # 按钮信号槽

    # 选择文件
    def select(self):
        filepath = easygui.fileopenbox()
        self.label.setText(filepath)

    # 执行
    def run(self):
        self.plainTextEdit.setPlainText('开始执行...')
        pass


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    myshow = MyWindow()
    myshow.show()
    sys.exit(app.exec_())
