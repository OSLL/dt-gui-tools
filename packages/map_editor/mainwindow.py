# -*- coding: utf-8 -*-
import codecs

from duckietown_world.structure.bases import _Frame
from duckietown_world.structure.duckietown_map import DuckietownMap

import mapviewer
import map
from DTWorld import get_dt_world, get_new_dt_world
import duckietown_world.structure as st

from classes.mapTile import MapTile
from forms.start_info import StartInfoForm
from managerduckietownmaps import ManagerDuckietownMaps
from mapEditor import MapEditor
from main_design import *
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QMessageBox, QDesktopWidget, QFormLayout, QVBoxLayout, QLineEdit, QCheckBox, QGroupBox, \
    QLabel, QComboBox
from IOManager import *
import functools, json, copy
from infowindow import info_window
from layers.layer_type import LayerType
import logging
import utils
from classes.mapObjects import MapBaseObject as MapObject
from classes.mapObjects import GroundAprilTagObject
from layers.relations import get_layer_type_by_object_type
from tag_config import get_duckietown_types
from forms.new_tag_object import NewTagForm
from forms.default_forms import question_form_yes_no
from DTWorld import get_dt_world
from duckietown_world.structure.objects import Watchtower, Citizen, Tile, TrafficSign, GroundTag, _TrafficSign

logger = logging.getLogger('root')
TILE_TYPES = ('block', 'road')
DEFAULT_TILE_SIZE = 0.585

# pyuic5 main_design.ui -o main_design.py

_translate = QtCore.QCoreApplication.translate
EPS = .1  # step for move

rot_val = {'E': 0, 'S': 90, 'W': 180, 'N': 270, None: 0}


class duck_window(QtWidgets.QMainWindow):
    map = None
    mapviewer = None
    info_json = None
    editor = None
    drawState = ''
    copyBuffer = [[]]

    def __init__(self, args, elem_info="doc/info.json"):
        super().__init__()
        # active items in editor
        self.active_items = []
        self.dm = get_dt_world()
        self.tile_size = DEFAULT_TILE_SIZE
        self.duckie_manager = ManagerDuckietownMaps()
        self.duckie_manager.add_map("maps/empty", self.dm)
        dm2_test = get_new_dt_world("maps/test")
        self.duckie_manager.add_map("maps/test", dm2_test)

        #  additional windows for displaying information
        self.author_window = info_window()
        self.param_window = info_window()
        self.mater_window = info_window()

        #  The brush button / override the closeEvent
        self.brush_button = QtWidgets.QToolButton()
        self.closeEvent = functools.partial(self.quit_program_event)

        # Set locale
        self.locale = args.locale

        # Set debug mode
        self.debug_mode = args.debug

        # Load element's info
        self.info_json = json.load(codecs.open(elem_info, "r", "utf-8"))

        # Loads info about types from duckietown
        self.duckietown_types_apriltags = get_duckietown_types()
        #####  Forms   #############
        self.new_tag_class = NewTagForm(self.duckietown_types_apriltags)
        self.init_info_form = StartInfoForm()
        ############################
        map_name = "maps/tm1"
        self.dm = get_dt_world(map_name)
        self.map = map.DuckietownMap()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        viewer = mapviewer.MapViewer()
        self.editor = MapEditor(self.map, self.mapviewer)
        viewer.setMap(self.map)
        self.mapviewer = viewer
        viewer.setMinimumSize(540, 540)
        self.ui.horizontalLayout.addWidget(viewer)
        viewer.repaint()
        self.initUi()

        init_map(self)
        self.update_layer_tree()

    def get_translation(self, elem):
        """Gets info about the element based on self.locale
        If local doesn't exist, return locale='en'

        :param self
        :param elem: dict, information about elements (or category), that contains translation
        :return: dict(). Dict with translation based on the self.locale
        """
        if self.locale in elem['lang']:
            return elem['lang'][self.locale]
        else:
            logger.debug("duck_window.get_translation. No such locale: {}".format(self.locale))
            return elem['lang']['en']

    def initUi(self):
        self.center()
        self.show()

        #  Initialize button objects
        create_map = self.ui.create_new
        open_map = self.ui.open_map
        save_map = self.ui.save_map
        save_map_as = self.ui.save_map_as
        export_png = self.ui.export_png
        calc_param = self.ui.calc_param
        calc_materials = self.ui.calc_materials
        about_author = self.ui.about_author
        exit = self.ui.exit
        change_blocks = self.ui.change_blocks
        change_info = self.ui.change_info
        change_map = self.ui.change_map
        change_layer = self.ui.change_layer

        #  Initialize floating blocks
        block_widget = self.ui.block_widget
        info_widget = self.ui.info_widget
        map_info_widget = self.ui.map_info_widget
        layer_info_widget = self.ui.layer_info_widget

        #  Signal from viewer
        self.mapviewer.selectionChanged.connect(self.selectionUpdate)
        self.mapviewer.editObjectChanged.connect(self.create_form)
        self.new_tag_class.apriltag_added.connect(self.add_apriltag)

        #  Assign actions to buttons
        create_map.triggered.connect(self.create_map_triggered)
        open_map.triggered.connect(self.open_map_triggered)
        save_map.triggered.connect(self.save_map_triggered)
        save_map_as.triggered.connect(self.save_map_as_triggered)
        export_png.triggered.connect(self.export_png_triggered)
        calc_param.triggered.connect(self.calc_param_triggered)
        calc_materials.triggered.connect(self.calc_materials_triggered)
        about_author.triggered.connect(self.about_author_triggered)
        exit.triggered.connect(self.exit_triggered)

        change_blocks.toggled.connect(self.change_blocks_toggled)
        change_info.toggled.connect(self.change_info_toggled)
        change_map.toggled.connect(self.change_map_toggled)
        change_layer.toggled.connect(self.toggle_layer_window)

        block_widget.closeEvent = functools.partial(self.blocks_event)
        info_widget.closeEvent = functools.partial(self.info_event)
        map_info_widget.closeEvent = functools.partial(self.map_event)
        layer_info_widget.closeEvent = functools.partial(self.close_layer_window_event)

        #  QToolBar setting
        tool_bar = self.ui.tool_bar

        a1 = QtWidgets.QAction(QtGui.QIcon("img/icons/new.png"), _translate("MainWindow", "New map"), self)
        a2 = QtWidgets.QAction(QtGui.QIcon("img/icons/open.png"), _translate("MainWindow", "Open map"), self)
        a3 = QtWidgets.QAction(QtGui.QIcon("img/icons/save.png"), _translate("MainWindow", "Save map"), self)
        a4 = QtWidgets.QAction(QtGui.QIcon("img/icons/save_as.png"), _translate("MainWindow", "Save map as"), self)
        a5 = QtWidgets.QAction(QtGui.QIcon("img/icons/png.png"), _translate("MainWindow", "Export to PNG"), self)

        b1 = QtWidgets.QAction(QtGui.QIcon("img/icons/copy.png"), _translate("MainWindow", "Copy"), self)
        b2 = QtWidgets.QAction(QtGui.QIcon("img/icons/cut.png"), _translate("MainWindow", "Cut"), self)
        b3 = QtWidgets.QAction(QtGui.QIcon("img/icons/insert.png"), _translate("MainWindow", "Paste"), self)
        b4 = QtWidgets.QAction(QtGui.QIcon("img/icons/delete.png"), _translate("MainWindow", "Delete"), self)
        b5 = QtWidgets.QAction(QtGui.QIcon("img/icons/undo.png"), _translate("MainWindow", "Undo"), self)
        b1.setShortcut("Ctrl+C")
        b2.setShortcut("Ctrl+X")
        b3.setShortcut("Ctrl+V")
        b4.setShortcut("Delete")
        b5.setShortcut("Ctrl+Z")

        c1 = QtWidgets.QAction(QtGui.QIcon("img/icons/rotate.png"), _translate("MainWindow", "Rotate"), self)
        c2 = QtWidgets.QAction(QtGui.QIcon("img/icons/trim.png"),
                               _translate("MainWindow", "Delete extreme empty blocks"), self)
        c1.setShortcut("Ctrl+R")
        c2.setShortcut("Ctrl+F")

        self.brush_button.setIcon(QtGui.QIcon("img/icons/brush.png"))
        self.brush_button.setCheckable(True)
        self.brush_button.setToolTip("Brush tool")
        self.brush_button.setShortcut("Ctrl+B")

        a1.triggered.connect(self.create_map_triggered)
        a2.triggered.connect(self.open_map_triggered)
        a3.triggered.connect(self.save_map_triggered)
        a4.triggered.connect(self.save_map_as_triggered)
        a5.triggered.connect(self.export_png_triggered)

        b1.triggered.connect(self.copy_button_clicked)
        b2.triggered.connect(self.cut_button_clicked)
        b3.triggered.connect(self.insert_button_clicked)
        b4.triggered.connect(self.delete_button_clicked)
        b5.triggered.connect(self.undo_button_clicked)

        c1.triggered.connect(self.rotateSelectedTiles)
        c2.triggered.connect(self.trimClicked)

        self.brush_button.clicked.connect(self.brush_mode)

        for elem in [[a1, a2, a3, a4, a5], [b1, b2, b3, b4, b5]]:
            for act in elem:
                tool_bar.addAction(act)
            tool_bar.addSeparator()
        tool_bar.addWidget(self.brush_button)
        tool_bar.addAction(c1)
        tool_bar.addAction(c2)

        # Setup Layer Tree menu
        self.ui.layer_tree.setModel(QtGui.QStandardItemModel())  # set item model for tree

        #  Customize the Blocks menu
        block_list_widget = self.ui.block_list
        block_list_widget.itemClicked.connect(self.item_list_clicked)
        block_list_widget.itemDoubleClicked.connect(self.item_list_double_clicked)

        #  Customize the Map Editor menu
        default_fill = self.ui.default_fill
        delete_fill = self.ui.delete_fill

        #  Fill out the list
        categories = self.info_json['categories']
        information = self.info_json['info']
        for group in categories:
            # add separator
            icon = "img/icons/galka.png"
            widget = QtWidgets.QListWidgetItem(QtGui.QIcon(icon), self.get_translation(group)['name'])
            widget.setData(0x0100, "separator")
            widget.setData(0x0101, group['id'])
            widget.setBackground(QtGui.QColor(169, 169, 169))
            block_list_widget.addItem(widget)
            # add elements
            for elem_id in group['elements']:
                widget = QtWidgets.QListWidgetItem(QtGui.QIcon(information[elem_id]['icon']),
                                                   self.get_translation(information[elem_id])['name'])
                widget.setData(0x0100, elem_id)
                widget.setData(0x0101, group['id'])
                block_list_widget.addItem(widget)
                # add tiles to fill menu
                if group['id'] in ("road", "block"):
                    default_fill.addItem(QtGui.QIcon(information[elem_id]['icon']),
                                         self.get_translation(information[elem_id])['name'], elem_id)
                    delete_fill.addItem(QtGui.QIcon(information[elem_id]['icon']),
                                        self.get_translation(information[elem_id])['name'], elem_id)

        default_fill.setCurrentText(self.get_translation(information["grass"])['name'])
        delete_fill.setCurrentText(self.get_translation(information["empty"])['name'])

        set_fill = self.ui.set_fill
        set_fill.clicked.connect(self.set_default_fill)

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    #  Create a new map
    def create_map_triggered(self):
        logger.debug(1)
        new_map(self)
        logger.debug("Length - {}".format(len(self.map.get_tile_layer().data)))
        self.mapviewer.offsetX = self.mapviewer.offsetY = 0
        self.mapviewer.scene().update()
        logger.debug("Creating a new map")
        self.update_layer_tree()

    #  Open map
    def open_map_triggered(self):
        logger.debug(2)
        self.editor.save(self.map)

        # dir_path = open_map(self)
        # self.dm = get_dt_world(dir_path)

        def init_info(info):
            i, j = int(info['x']), int(info['y'])
            self.tile_size = float(info['tile_size'])
            self.create_empty_map(i, j)
            self.dm.tile_maps['map_1'].x = self.tile_size
            self.dm.tile_maps['map_1'].y = self.tile_size
            # self.dm.tile_maps['map_1']
            self.mapviewer.tile_size = self.tile_size
            self.mapviewer.scene().update()
            self.update_layer_tree()

        self.init_info_form.send_info.connect(init_info)
        self.init_info_form.show()

        self.mapviewer.offsetX = self.mapviewer.offsetY = 0
        self.mapviewer.scene().update()
        self.update_layer_tree()

    #  Save map
    def save_map_triggered(self):
        save_map(self)
        logger.debug("Save")

    #  Save map as
    def save_map_as_triggered(self):
        path_folder = save_map_as(self)
        if path_folder:
            map_final = self.dm.dump(self.dm)
            # print(map_final)
            # for i in map_final:
            #    print('aaaa ', i)
            for layer_name in map_final:
                with open(path_folder + f'/{layer_name}.yaml', 'w+') as file:
                    file.write(map_final[layer_name])
            print('FINAL PATH, ', path_folder)

    #  Export to png
    def export_png_triggered(self):
        export_png(self)

    #  Calculate map characteristics
    def calc_param_triggered(self):

        text = get_map_specifications(self)
        self.show_info(self.param_window, _translate("MainWindow", "Map characteristics"), text)

    #  Calculate map materials
    def calc_materials_triggered(self):
        text = get_map_materials(self)
        self.show_info(self.mater_window, _translate("MainWindow", "Map material"), text)

    #  Help: About
    def about_author_triggered(self):
        text = '''
        - Select an object using the left mouse button\n
        - when object is selected you can change pos, using WASD: W(UP), A(LEFT), D(RIGHT), S(DOWN)\n
        - reset object tracking using `Q`\n
        - add apriltag using key `R`\n
        - Edit an object, click on it using the right mouse button\n
        - Authors:\n alskaa;\n dihindee;\n ovc-serega;\n HadronCollider;\n light5551;\n snush.\n\n Contact us on github!
        '''
        self.show_info(self.author_window, "About", text)

    #  Exit
    def exit_triggered(self):
        self.save_before_exit()
        QtCore.QCoreApplication.instance().quit()

    # Save map before exit
    def save_before_exit(self):
        if not self.debug_mode:
            ret = self.quit_MessageBox()
            if ret == QMessageBox.Cancel:
                return
            if ret == QMessageBox.Save:
                save_map(self)

    #  Hide Block menu
    def change_blocks_toggled(self):
        block = self.ui.block_widget
        if self.ui.change_blocks.isChecked():
            block.show()
            block.setFloating(False)
        else:
            block.close()

    #  Change button state
    def blocks_event(self, event):
        self.ui.change_blocks.setChecked(False)
        event.accept()

    #  Hide information menu
    def change_info_toggled(self):
        block = self.ui.info_widget
        if self.ui.change_info.isChecked():
            block.show()
            block.setFloating(False)
        else:
            block.close()

    #  Change button state
    def info_event(self, event):
        self.ui.change_info.setChecked(False)
        event.accept()

    #  Hide the menu about map properties
    def change_map_toggled(self):
        block = self.ui.map_info_widget
        if self.ui.change_map.isChecked():
            block.show()
            block.setFloating(False)
        else:
            block.close()

    #  Change button state
    def map_event(self, event):
        self.ui.change_map.setChecked(False)
        event.accept()

    # Layer window

    def toggle_layer_window(self):
        """
        Toggle layers window by `View -> Layers`
        :return: -
        """
        block = self.ui.layer_info_widget
        if self.ui.change_layer.isChecked():
            block.show()
            block.setFloating(False)
        else:
            block.close()

    def close_layer_window_event(self, event):
        """
        Reset flag `View -> Layers` when closing layers window
        :param event: closeEvent
        :return: -
        """
        self.ui.change_layer.setChecked(False)
        event.accept()

    def layer_tree_clicked(self):
        pass

    def layer_tree_double_clicked(self):
        pass

    def update_layer_tree(self):
        """
        Update layer tree.
        Show layer's elements as children in hierarchy (except tile layer)
        :return: -
        """
        print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        def signal_check_state(item):
            """
            update visible state of layer.
            :return: -
            """

            #layer = self.map.get_layer_by_type_name(item.text())
            #print(item.text(), layer)
            #if not layer:

            #    logger.debug("Not found layer: {}".format(item.text()))
            #    return

            #layer.visible = not layer.visible
            #logger.debug('Layer: {}; visible: {}'.format(item.text(), layer.visible))
            #self.map.set_layer(layer)
            dm = self.duckie_manager.get_map(item.text())
            self.reset_duckietown_map(dm)
            self.mapviewer.scene().update()
            layer_tree_view.clearSelection()
            #layer_tree_view.expandAll()

            #self.update_layer_tree()

        #def reset_ui_dm(item):
        #    print('1 ', item.text())
        #    dm = self.duckie_manager.get_map(item.text())
        #    print(dm)
        #    self.reset_duckietown_map(dm)
        #    self.mapviewer.scene().update()
        #    print('2')

        layer_tree_view = self.ui.layer_tree
        item_model = layer_tree_view.model()
        item_model.clear()
        print('waws clear')
        try:
            item_model.itemChanged.disconnect()
        except TypeError:
            pass  # only 1st time in update_layer_tree
        item_model.itemChanged.connect(signal_check_state)
        #item_model.itemChanged.connect(signal_check_state)
        #item_model.itemChanged.connect(reset_ui_dm)
        item_model.setHorizontalHeaderLabels(['Name'])
        root_item = layer_tree_view.model().invisibleRootItem()
        #for map_name in self.duckie_manager.get_maps_name():
        #    layer_item = QtGui.QStandardItem(str(map_name))
        #    layer_item.setCheckable(True)
        #    layer_item.setCheckState(QtCore.Qt.Checked)
        #    root_item.appendRow(layer_item)
        #    layer_item.appendRow(QtGui.QStandardItem(map_name))
        #    #layer_item.sortChildren(0)


        #for layer in self.map.layers:
        for map_name in self.duckie_manager.get_maps_name():
            layer_item = QtGui.QStandardItem(str(map_name))
            layer_item.setCheckable(True)
            layer_item.setCheckState(QtCore.Qt.Unchecked)
            layer_item.setCheckState(QtCore.Qt.Checked if self.duckie_manager.is_active == map_name else QtCore.Qt.Unchecked)
            root_item.appendRow(layer_item)
            #if layer.type == LayerType.TILES:
            #    tile_elements = []
            #    for row in layer.data:
            #        for tile in row:
            #            tile_elements.append(tile.kind)
            #    layer_elements = utils.count_elements(tile_elements)
            #elif layer.type in (LayerType.TRAFFIC_SIGNS, LayerType.GROUND_APRILTAG):
            #    layer_elements = utils.count_elements(['{}{}'.format(elem.kind, elem.tag_id) for elem in layer.data])
            #else:
            #    layer_elements = utils.count_elements([elem.kind for elem in layer.data])
            #for kind, counter in layer_elements.most_common():
            #    item = QtGui.QStandardItem("{} ({})".format(kind, counter))
            #    layer_item.appendRow(item)
            layer_item.sortChildren(0)


        layer_tree_view.expandAll()

    #  MessageBox to exit
    def quit_MessageBox(self):
        reply = QMessageBox(self)
        reply.setIcon(QMessageBox.Question)
        reply.setWindowTitle(_translate("MainWindow", "Exit"))
        reply.setText(_translate("MainWindow", "Exit"))
        reply.setInformativeText(_translate("MainWindow", "Save and exit?"))
        reply.setStandardButtons(QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
        reply.setDefaultButton(QMessageBox.Save)
        ret = reply.exec()
        return ret

    #  Program exit event
    def quit_program_event(self, event):
        self.save_before_exit()

        #  Close additional dialog boxes
        self.author_window.exit()
        self.param_window.exit()
        self.mater_window.exit()

        event.accept()

    def create_empty_map(self, i_size: int, j_size: int) -> None:
        for i in range(i_size):
            for j in range(j_size):
                tile = Tile("map_1/tile_{}_{}".format(i, j))
                tile.obj.i = i
                tile.obj.j = j
                tile.frame.pose.x = i + 0.5
                tile.frame.pose.y = j + 0.5
                tile.frame.relative_to = 'map_1'
                tile.frame.dm = self.dm
                self.dm.add(tile)

    #  Handle a click on an item from a list to a list
    def item_list_clicked(self):
        list = self.ui.block_list
        name = list.currentItem().data(0x0100)
        type = list.currentItem().data(0x0101)

        if name == "separator":
            list.currentItem().setSelected(False)

            for i in range(list.count()):
                elem = list.item(i)
                if type == elem.data(0x0101):
                    if name == elem.data(0x0100):
                        icon = QtGui.QIcon("img/icons/galka.png") if list.item(i + 1).isHidden() else \
                            QtGui.QIcon("img/icons/galka_r.png")
                        elem.setIcon(icon)
                    else:
                        elem.setHidden(not elem.isHidden())
        else:
            elem = self.info_json['info'][name]
            info_browser = self.ui.info_browser
            info_browser.clear()
            text = "{}:\n {}\n{}:\n{}".format(_translate("MainWindow", "Name"), list.currentItem().text(),
                                              _translate("MainWindow", "Description"),
                                              self.get_translation(elem)['info'])
            if elem["type"] == "block":
                text += "\n\n{}: {} {}".format(_translate("MainWindow", "Road len"), elem["length"],
                                               _translate("MainWindow", "sm"))
                text += " Tape:\n"
                text += " {}: {} {}\n".format(_translate("MainWindow", "Red"), elem["red"],
                                              _translate("MainWindow", "sm"))
                text += " {}: {} {}\n".format(_translate("MainWindow", "Yellow"), elem["yellow"],
                                              _translate("MainWindow", "sm"))
                text += " {}: {} {}\n".format(_translate("MainWindow", "White"), elem["white"],
                                              _translate("MainWindow", "sm"))
            info_browser.setText(text)

    #  Double click initiates as single click action
    def item_list_double_clicked(self):
        item_ui_list = self.ui.block_list
        item_name = item_ui_list.currentItem().data(0x0100)
        item_type = item_ui_list.currentItem().data(0x0101)

        if item_name == "separator":
            item_ui_list.currentItem().setSelected(False)
        else:
            if item_type in TILE_TYPES:
                self.ui.default_fill.setCurrentText(self.get_translation(self.info_json['info'][item_name])['name'])
                logger.debug("Set {} for brush".format(item_name))
            else:
                # save map before adding object
                self.editor.save(self.map)
                # adding object
                print(item_name)
                print(self.info_json['info'][item_name]['type'])
                type_of_element = self.info_json['info'][item_name]['type']
                obj = None
                if item_name == "duckie":
                    obj = Citizen(self.get_random_name("map_1/duckie"), x=1, y=1)
                elif item_name == "watchtower":
                    obj = Watchtower(self.get_random_name("map_1/watchtower"), x=1, y=1)
                elif type_of_element == "sign":
                    obj = TrafficSign(self.get_random_name("map_1/{}".format(item_name)), x=1, y=1)
                    obj.obj.type = item_name
                elif item_name == "apriltag":
                    obj = GroundTag(self.get_random_name("map_1/grountag"), x=1, y=1)
                if obj:
                    obj.frame.relative_to = "map_1"
                    self.dm.add(obj)
                # self.map.add_objects_to_map([dict(kind=item_name, pos=(.0, .0), rotate=0, height=1,
                #                                  optional=False, static=True)], self.info_json['info'])

                # TODO: need to understand what's the type and create desired class, not general
                # also https://github.com/moevm/mse_visual_map_editor_for_duckietown/issues/122
                # (for args, that can be edited and be different between classes)
                self.mapviewer.scene().update()
                logger.debug("Add {} to map".format(item_name))
            self.update_layer_tree()

    #  Reset to default values
    def set_default_fill(self):
        default_fill = self.ui.default_fill.currentData()
        delete_fill = self.ui.delete_fill.currentData()
        # TODO установка занчений по умолчанию
        logger.debug("{}; {}".format(default_fill, delete_fill))

    #  Copy
    def copy_button_clicked(self):
        if self.brush_button.isChecked():
            self.brush_button.click()
        self.drawState = 'copy'
        self.copyBuffer = copy.copy(self.mapviewer.tileSelection)
        logger.debug("Copy")

    #  Cut
    def cut_button_clicked(self):
        if self.brush_button.isChecked():
            self.brush_button.click()
        self.drawState = 'cut'
        self.copyBuffer = copy.copy(self.mapviewer.tileSelection)
        logger.debug("Cut")

    #  Paste
    def insert_button_clicked(self):
        if len(self.copyBuffer) == 0:
            return
        self.editor.save(self.map)
        if self.drawState == 'copy':
            self.editor.copySelection(self.copyBuffer, self.mapviewer.tileSelection[0], self.mapviewer.tileSelection[1],
                                      MapTile(self.ui.delete_fill.currentData()))
        elif self.drawState == 'cut':
            self.editor.moveSelection(self.copyBuffer, self.mapviewer.tileSelection[0], self.mapviewer.tileSelection[1],
                                      MapTile(self.ui.delete_fill.currentData()))
        self.mapviewer.scene().update()
        self.update_layer_tree()

    #  Delete
    def delete_button_clicked(self):
        if not self.map.get_tile_layer().visible:
            return
        self.editor.save(self.map)
        self.editor.deleteSelection(self.mapviewer.tileSelection, MapTile(self.ui.delete_fill.currentData()))
        self.mapviewer.scene().update()
        self.update_layer_tree()

    #  Undo
    def undo_button_clicked(self):
        self.editor.undo()
        self.mapviewer.scene().update()
        self.update_layer_tree()

    #  Brush mode
    def brush_mode(self):
        if self.brush_button.isChecked():
            self.drawState = 'brush'
        else:
            self.drawState = ''

    def keyPressEvent(self, e):
        selection = self.mapviewer.raw_selection
        item_layer = self.map.get_objects_from_layers()  # TODO: add self.current_layer for editing only it's objects?
        new_selected_obj = False
        for item in item_layer:
            x, y = item.position
            if x > selection[0] and x < selection[2] and y > selection[1] and y < selection[3]:
                if item not in self.active_items:
                    self.active_items.append(item)
                    new_selected_obj = True
        if new_selected_obj:
            # save map if new objects are selected
            self.editor.save(self.map)
        key = e.key()
        if key == QtCore.Qt.Key_Q:
            # clear object buffer
            self.active_items = []
            self.mapviewer.raw_selection = [0] * 4
        elif key == QtCore.Qt.Key_R:
            self.new_tag_class.create_form()
        elif key == QtCore.Qt.Key_H:
            #print(self.duckie_manager.get_maps_name())
            for map_name in self.duckie_manager.get_maps_name():
                if map_name == "maps/test":
                    self.reset_duckietown_map(self.duckie_manager.get_map(map_name))
                #print(map_name)
                #print(self.duckie_manager.get_map(map_name))

        if self.active_items:
            if key == QtCore.Qt.Key_Backspace:
                # delete object
                if question_form_yes_no(self, "Deleting objects", "Delete objects from map?") == QMessageBox.Yes:
                    # save map before deleting objects
                    self.editor.save(self.map)
                    for item in self.active_items:
                        object_type = self.info_json['info'][item.kind]['type']
                        layer = self.map.get_layer_by_type(get_layer_type_by_object_type(object_type))
                        layer.remove_object_from_layer(item)
                    self.active_items = []
                    self.mapviewer.scene().update()
                    self.update_layer_tree()
                return
            for item in self.active_items:
                logger.debug("Name of item: {}; X - {}; Y - {};".format(item.kind, item.position[0], item.position[1]))
                if key == QtCore.Qt.Key_W:
                    item.position[1] -= EPS
                elif key == QtCore.Qt.Key_S:
                    item.position[1] += EPS
                elif key == QtCore.Qt.Key_A:
                    item.position[0] -= EPS
                elif key == QtCore.Qt.Key_D:
                    item.position[0] += EPS
                elif key == QtCore.Qt.Key_E:
                    if len(self.active_items) == 1:
                        self.create_form(self.active_items[0])
                    else:
                        logger.debug("I can't edit more than one object!")
        self.mapviewer.scene().update()

    def create_form(self, active_object_data: tuple):
        '''
                def accept():
            if 'tag_type' in edit_obj:
                tag_type = edit_obj['tag_type'].text()
                if 'tag_id' in edit_obj and (not edit_obj['tag_id'].text().isdigit() or int(edit_obj['tag_id'].text()) not in self.duckietown_types_apriltags[tag_type]):
                    msgBox = QMessageBox()
                    msgBox.setText("tag id or tag type is uncorrect!")
                    msgBox.exec()
                    return
                if tag_type not in self.duckietown_types_apriltags.keys() or int(edit_obj['tag_id'].text()) not in self.duckietown_types_apriltags[tag_type]:
                    msgBox = QMessageBox()
                    msgBox.setText("tag id or tag type is uncorrect!")
                    msgBox.exec()
                    return
            elif 'tag_id' in edit_obj:
                if not edit_obj['tag_id'].text().isdigit() or not int(edit_obj['tag_id'].text()) in self.duckietown_types_apriltags['TrafficSign']:
                    msgBox = QMessageBox()
                    msgBox.setText("tag id is uncorrect!")
                    msgBox.exec()
                    return
            for attr_name, attr in editable_attrs.items():
                if attr_name == 'pos':
                    active_object.position[0] = float(edit_obj['x'].text())
                    active_object.position[1] = float(edit_obj['y'].text())
                    continue
                if type(attr) == bool:
                    active_object.__setattr__(attr_name, edit_obj[attr_name].isChecked())
                    continue
                if type(attr) == float:
                    active_object.__setattr__(attr_name, float(edit_obj[attr_name].text()))
                if type(attr) == int:
                    active_object.__setattr__(attr_name, int(edit_obj[attr_name].text()))
                else:
                    active_object.__setattr__(attr_name, edit_obj[attr_name].text())
            dialog.close()
            self.mapviewer.scene().update()
            self.update_layer_tree()

        def reject():
            dialog.close()

        '''
        active_object, (name, tp) = active_object_data
        assert tp is _Frame

        def accept():
            active_object.pose.x = float(edit_obj['x'].text())
            active_object.pose.y = float(edit_obj['y'].text())
            for key in editable_values:
                print(key)
                new_value = edit_obj[key].text()
                if new_value.isdigit():
                    new_value = int(new_value)
                try:
                    if isinstance(new_value, str):
                        new_value = float(new_value)
                except ValueError:
                    pass
                obj[key] = new_value

            dialog.close()
            self.mapviewer.scene().update()
            self.update_layer_tree()

        def reject():
            dialog.close()

        # work version
        info_object = self.dm.get_objects_by_name(name)
        del info_object[(name, tp)]
        _, type_object = list(info_object.keys())[0]
        obj = info_object[(name, type_object)]

        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle('Change attribute of object')
        # buttonbox
        buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(accept)
        buttonBox.rejected.connect(reject)
        # form
        formGroupBox = QGroupBox("Change attribute's object: {}".format(""))

        layout = QFormLayout()
        # editable_attrs = active_object.get_editable_attrs()
        edit_obj = {}
        combo_id = QComboBox(self)

        # def change_combo_id(value):
        #    combo_id.clear()
        #    combo_id.addItems([str(i) for i in self.duckietown_types_apriltags[value]])
        #    combo_id.setEditText(str(self.duckietown_types_apriltags[value][0]))

        x_edit = QLineEdit(str(active_object.pose.x))
        y_edit = QLineEdit(str(active_object.pose.y))
        edit_obj['x'] = x_edit
        edit_obj['y'] = y_edit
        layout.addRow(QLabel("{}.X".format("pose")), x_edit)
        layout.addRow(QLabel("{}.Y".format("pose")), y_edit)
        editable_values = obj.dict()
        print('ATTR SHOW: ', editable_values)
        for attr_name in sorted(editable_values.keys()):
            new_edit = QLineEdit(str(editable_values[attr_name]))
            edit_obj[attr_name] = new_edit
            layout.addRow(QLabel("{}".format(attr_name)), new_edit)
        '''
        for attr_name in sorted(editable_attrs):
            attr = editable_attrs[attr_name]
            if attr_name == 'pos':
                x_edit = QLineEdit(str(attr[0]))
                y_edit = QLineEdit(str(attr[1]))
                edit_obj['x'] = x_edit
                edit_obj['y'] = y_edit
                layout.addRow(QLabel("{}.X".format(attr_name)), x_edit)
                layout.addRow(QLabel("{}.Y".format(attr_name)), y_edit)
                continue
            elif attr_name == 'tag_id':
                edit = QLineEdit(str(attr))
                edit_obj[attr_name] = edit
                tag_id = int(attr)
                type_id = list(self.duckietown_types_apriltags.keys())[0]
                for type_sign in self.duckietown_types_apriltags.keys():
                    if tag_id in self.duckietown_types_apriltags[type_sign]:
                        type_id = type_sign
                        break
                
                combo_id.addItems([str(i) for i in self.duckietown_types_apriltags[type_id]])
                combo_id.setLineEdit(edit)
                combo_id.setEditText(str(attr))
                layout.addRow(QLabel(attr_name), combo_id)
                continue
            elif attr_name == 'tag_type':
                edit = QLineEdit(str(attr))
                edit_obj[attr_name] = edit
                combo_type = QComboBox(self)
                combo_type.addItems([str(i) for i in self.duckietown_types_apriltags.keys()])
                combo_type.activated[str].connect(change_combo_id)
                combo_type.setLineEdit(edit)
                combo_type.setEditText(attr)
                layout.addRow(QLabel(attr_name), combo_type)
                continue
            if type(attr) == bool:
                check = QCheckBox()
                check.setChecked(attr)
                edit_obj[attr_name] = check
                layout.addRow(QLabel(attr_name), check)
                continue
            edit = QLineEdit(str(attr))
            edit_obj[attr_name] = edit
            layout.addRow(QLabel(attr_name), edit)
        '''
        formGroupBox.setLayout(layout)
        # layout
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(formGroupBox)
        mainLayout.addWidget(buttonBox)
        dialog.setLayout(mainLayout)
        dialog.exec_()

    def rotateSelectedTiles(self):
        self.editor.save(self.map)
        is_selected_tile = self.mapviewer.is_selected_tile
        tiles = self.dm.tiles.only_tiles()
        for i in range(len(tiles)):
            for j in range(len(tiles[0])):
                tile = tiles[i][j]
                if is_selected_tile(tile):
                    orien_val = (rot_val[tile.orientation] + 90) % 360
                    for key in rot_val:
                        if rot_val[key] == orien_val:
                            tile.orientation = key
            self.mapviewer.scene().update()

    def add_apriltag(self, apriltag: GroundAprilTagObject):
        layer = self.map.get_layer_by_type(LayerType.GROUND_APRILTAG)
        if layer is None:
            self.map.add_layer_from_data(LayerType.GROUND_APRILTAG, [apriltag])
        else:
            self.map.add_elem_to_layer_by_type(LayerType.GROUND_APRILTAG, apriltag)
        self.update_layer_tree()
        self.mapviewer.scene().update()

    def trimClicked(self):
        self.editor.save(self.map)
        self.editor.trimBorders(True, True, True, True, MapTile(self.ui.delete_fill.currentData()))
        self.mapviewer.scene().update()
        self.update_layer_tree()

    def selectionUpdate(self):
        is_selected_tile = self.mapviewer.is_selected_tile
        if self.drawState == 'brush':
            self.editor.save(self.map)  # TODO: CTRL+Z need to fix because dt-world
            tiles = self.dm.tiles.only_tiles()
            for i in range(len(tiles)):
                for j in range(len(tiles[0])):
                    tile = tiles[i][j]
                    if is_selected_tile(tile):
                        tile.type = self.ui.default_fill.currentData()
                        tile.orientation = 'N'
        self.update_layer_tree()
        self.mapviewer.scene().update()

    def reset_duckietown_map(self, new_dm: DuckietownMap):
        self.dm = new_dm
        self.mapviewer.dm = new_dm
        #self.update_layer_tree()
        self.mapviewer.scene().update()

    def get_random_name(self, begin):
        return "{}_{}".format(
            begin,
            np.random.randint(1000)
        )

    def show_info(self, name, title, text):
        name.set_window_name(title)
        name.set_text(text)
        name.show()
