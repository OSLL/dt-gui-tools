# -*- coding: utf-8 -*-
import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog
from map_parser import *
from utils import get_list_dir_with_path
from layers.layer_type import get_layer_type_by_value


def init_map(parent: QtWidgets.QWidget):
    input_map = './maps/empty.yaml'
    if new_map:
        map_info = data_from_file(input_map)
        parent.map.set_tile_layer(tiles_to_objects(map_info['tiles']))
        param = map_info['objects'] if 'objects' in map_info else None
        parent.map.clear_objects_layers()
        parent.map.add_objects_to_map(map_objects_to_objects(param), parent.info_json['info'])
        parent.map.gridSize = 58.5


def open_map(parent: QtWidgets.QWidget):
    input_map_dir = QFileDialog.getExistingDirectory(parent, 'Open map from directory', '.',  QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)
    if input_map_dir:
        parent.map.name = input_map_dir
        parent.map.layers = []
        for filename, path in get_list_dir_with_path(input_map_dir):
            # load layer
            layer_info = data_from_file(path)  # ['data'] = list, ['type'] = type
            # extract lab code from layer's filename
            lab_code = filename[len(layer_info['type'])+1:-len('.yaml')]
            # get layer_type
            layer_type = get_layer_type_by_value(layer_info['type'])
            # get layer data
            layer_data = layer_info['data']
            # add layer
            if layer_type == LayerType.TILES:
                layer_data = tiles_to_objects(layer_data)
                parent.map.gridSize = 100 * layer_info['tile_size']                
                if not parent.map.add_layer_from_data(layer_type=layer_type, layer_data=layer_data, layer_name=lab_code):
                    parent.map.set_tile_layer(layer_data)
            else:
                parent.map.add_objects_to_layer(objects=layer_data, layer_type=layer_type, layer_name=lab_code) 


def get_lab_code(parent): return QtWidgets.QInputDialog.getText(parent, "Lab code", "Enter Lab's code for map:")


def save_map_as(parent: QtWidgets.QWidget):
    if parent.map.layers:
        output_map_dir = QFileDialog.getExistingDirectory(parent, 'Save map to directory', '.',  QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)
        if output_map_dir:
            parent.map.name = output_map_dir
            lab_code, ok = get_lab_code(parent)
            if ok:
                map_to_yaml(parent.map, output_map_dir, lab_code)


def save_map(parent: QtWidgets.QWidget):
    if parent.map.name:
        if parent.map.layers:
            map_to_yaml(parent.map, parent.map.name)
    else:
        save_map_as(parent)


def export_png(parent: QtWidgets.QWidget):
    if parent.map.get_tile_layer():
        output_map = QFileDialog.getSaveFileName(parent, 'Save file', '.', filter='PNG file (*.png)')[0]
        if output_map:
            map_to_png(parent.mapviewer, output_map)


def new_map(parent: QtWidgets.QWidget):
    new_map_dir = QFileDialog.getExistingDirectory(parent, 'Save map to directory', '.',  QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)
    input_map = './maps/empty.yaml'
    if new_map_dir:
        parent.map.name = new_map_dir
        map_info = data_from_file(input_map)
        parent.map.set_tile_layer(tiles_to_objects((map_info['tiles'])))
        param = map_info['objects'] if 'objects' in map_info else None
        parent.map.set_item_layer(map_objects_to_objects(param))
        map_to_yaml(parent.map, new_map_dir)


def get_map_specifications(parent: QtWidgets.QWidget):
    return specifications_of_map(parent.map, parent.info_json['info'])


def get_map_materials(parent: QtWidgets.QWidget):
    return materials_of_map(parent.map, parent.info_json['info'])
