from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QComboBox, QDialog, QGroupBox, QDialogButtonBox, QFormLayout,QVBoxLayout, QLineEdit, QMessageBox
from classes.mapObjects import GroundAprilTagObject

class NewTagForm(QDialog):
    apriltag_added = QtCore.pyqtSignal(GroundAprilTagObject)
    def __init__(self, tags):
        self.tags = tags
        super().__init__()
        self.init_UI()

    def dialog_accept(self):
        tag_type = self.combo_type.currentText()
        try:
            tag_id = int(self.combo_id.currentText())
        except Exception:
            msgBox = QMessageBox()
            msgBox.setText("ID - {} should be only int".format(self.combo_id.currentText()))
            msgBox.exec()
            return

        if tag_id in self.tags[self.combo_type.currentText()]:
            self.apriltag_added.emit(GroundAprilTagObject(**dict(kind="apriltag", pose=(1.0, 1.0), tag_id=tag_id)))
            self.close()
        else:
            msgBox = QMessageBox()
            msgBox.setText("No such tag {} in {}".format(tag_id, self.combo_type.currentText()))
            msgBox.exec()

    def dialog_reject(self):
        self.close()
    
    def second_combo_box_changed(self, value):
        self.lineEdit.setText(value)

    def init_UI(self):
        self.setWindowTitle('New tag')
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.dialog_accept)   
        buttonBox.rejected.connect(self.dialog_reject)

        formGroupBox = QGroupBox("")

        layout = QFormLayout()
        self.combo_type = QComboBox(self)
        self.combo_type.addItems(self.tags.keys())
        self.combo_type.activated[str].connect(self.change_type)
        layout.addRow(self.combo_type)

        
        self.lineEdit = QLineEdit(self)
        self.lineEdit.setText("0")

        self.combo_id = QComboBox(self)
        self.combo_id.addItems([str(i) for i in self.tags['TrafficSign']])
        self.combo_id.currentTextChanged.connect(self.second_combo_box_changed)
        self.combo_id.setLineEdit(self.lineEdit)

        layout.addRow(self.combo_id)
        formGroupBox.setLayout(layout)

        # layout
        mainLayout = QVBoxLayout() 
        mainLayout.addWidget(formGroupBox)
        mainLayout.addWidget(buttonBox)
        self.setLayout(mainLayout)

    def create_form(self):
        self.exec_()

    def change_type(self, text):
        self.combo_id.clear()
        self.combo_id.addItems([str(i) for i in self.tags[text]])
        