from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QComboBox, QDialog, QGroupBox, QDialogButtonBox, QFormLayout,QVBoxLayout
from classes.mapObjects import GroundAprilTagObject

class NewTagForm(QDialog):
    apriltag_added = QtCore.pyqtSignal(list)
    def __init__(self, tags):
        self.tags = tags
        super().__init__()
        self.init_UI()

    def dialog_accept(self):
        tag_type = self.combo_type.currentText()
        tag_id =  int(self.combo_id.currentText())
        print(self.combo_type.currentText(), self.combo_id.currentText())
        '''
        self.apriltag_added.emit(GroundAprilTagObject({
            "kind": "apriltag_300",
            "pos": [2.0, 0.0],
            "rotate": 0,
            "static": True,
            "height": 1,
            "optional": False,
            "tag_type": tag_type,
            "tag_id": tag_id
        }))
        '''
        self.apriltag_added.emit([dict(kind="apriltag_300",pos=(1.0, 1.0), rotate=0, height=1,
                                                  optional=False, static=True, tag_type=tag_type, tag_id=tag_id)])
        #apriltag = GroundAprilTagObject({})
        self.close()

    def dialog_reject(self):
        self.close()
    
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

        self.combo_id = QComboBox(self)
        self.combo_id.addItems([str(i) for i in self.tags['TrafficSign']])
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
        