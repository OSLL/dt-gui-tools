from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QComboBox, QDialog, QGroupBox, QDialogButtonBox, QFormLayout, QVBoxLayout, \
    QLineEdit, QMessageBox
from PyQt5.QtWidgets import QMessageBox, QMainWindow, QWidget, QPlainTextEdit


class SerializeForm(QDialog):

    def __init__(self, text):
        super().__init__()
        self.text = text
        self.init_UI()

    def dialog_accept(self):
        self.close()

    def dialog_reject(self):
        self.close()

    def init_UI(self):
        text = QPlainTextEdit(None)
        text.insertPlainText(self.text)
        text.resize(800, 800)
        # layout
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(text)
        self.setLayout(mainLayout)

    def create_form(self):
        self.exec_()

