# -*- coding: utf-8 -*-
import numpy as np

from classes.mapTile import MapTile
from mapviewer import MapViewer
from layers.layer_type import LayerType
from PyQt5 import QtGui, QtCore
import logging
import yaml

logger = logging.getLogger('root')


rotation_val = {0: 'E', 90: 'S', 180: 'W', 270: 'N'}
_translate = QtCore.QCoreApplication.translate


def get_map_objects(map):
    result = ''
    padding = '   '
    padding2 = padding + padding
    barrier = 0
    building = 0
    bus = 0
    cone = 0
    duckie = 0
    duckiebot = 0
    house = 0
    tree = 0
    trafficlight = 0
    truck = 0
    item_layer = map.get_item_layer().data
    if item_layer:
        for object in item_layer:
            if object.kind == 'barrier':
                barrier += 1
            elif object.kind == 'trafficlight':
                trafficlight += 1
            elif object.kind == 'tree':
                tree += 1
            elif object.kind == 'building':
                building += 1
            elif object.kind == 'bus':
                bus += 1
            elif object.kind == 'cone':
                cone += 1
            elif object.kind == 'duckie':
                duckie += 1
            elif object.kind == 'duckiebot':
                duckiebot += 1
            elif object.kind == 'house':
                house += 1
            elif object.kind == 'truck':
                truck += 1

    result += '{}\n'.format(_translate("MainWindow", "Objects"))
    if barrier:
        result += '{}{}: {} {}\n'.format(padding, _translate("MainWindow", "Barrier"), barrier, _translate("MainWindow", "pcs"))
    if building:
        result += '{}{}: {} {}\n'.format(padding, _translate("MainWindow", "Building"), building, _translate("MainWindow", "pcs"))
    if bus:
        result += '{}{}: {} {}\n'.format(padding, _translate("MainWindow", "Bus"), bus, _translate("MainWindow", "pcs"))
    if truck:
        result += '{}{}: {} {}\n'.format(padding, _translate("MainWindow", "Truck"), truck, _translate("MainWindow", "pcs"))
    if cone:
        result += '{}{}: {} {}\n'.format(padding, _translate("MainWindow", "Cone"), cone, _translate("MainWindow", "pcs"))
    if house:
        result += '{}{}: {} {}\n'.format(padding, _translate("MainWindow", "House"), house, _translate("MainWindow", "pcs"))
    if tree:
        result += '{}{}: {} {}\n'.format(padding, _translate("MainWindow", "Tree"), tree, _translate("MainWindow", "pcs"))
    if duckie:
        result += '{}{}: {} {}\n'.format(padding, _translate("MainWindow", "Duckie"), duckie, _translate("MainWindow", "pcs"))
    if duckiebot:
        result += '{}{}: {} {}\n'.format(padding, _translate("MainWindow", "Duckiebot"), duckiebot, _translate("MainWindow", "pcs"))
    if trafficlight:
        result += '{}{}: {} {}\n'.format(padding, _translate("MainWindow", "Trafficlight"), trafficlight, _translate("MainWindow", "pcs"))
    return result


def get_map_elements(map):
    result = ''
    padding = '   '
    padding2 = padding + padding

    sign_no_right_turn = sign_no_left_turn = 0
    sign_oneway_right = sign_oneway_left = 0
    sign_right_T_intersect = sign_left_T_intersect = 0
    sign_duck = 0
    sign_4_way = sign_T = parking = 0
    sign_do_not_enter = 0
    sign_pedestrian = sign_stop = sign_yield = 0
    sign_t_light_ahead = 0

    count_of_curve = count_of_str = 0
    count_of_3way = count_of_4way = 0
    count_of_floor = count_of_grass = count_of_asphalt = 0

    for tile in np.array(map.get_tile_layer().data).flat:
        if '4way' in tile.kind:
            count_of_4way += 1
        elif '3way' in tile.kind:
            count_of_3way +=1
        elif 'curve' in tile.kind:
            count_of_curve += 1
        elif 'straight' in tile.kind:
            count_of_str +=1
        elif 'grass' in tile.kind:
            count_of_grass +=1
        elif 'floor' in tile.kind:
            count_of_floor += 1
        elif 'asphalt' in tile.kind:
            count_of_asphalt +=1

    item_layer = map.get_item_layer().data
    if item_layer:
        for object in item_layer:
            if object.kind == 'sign_4_way_intersect':
                sign_4_way += 1
            elif object.kind == 'sign_right_T_intersect':
                sign_right_T_intersect += 1
            elif object.kind == 'sign_left_T_intersect':
                sign_left_T_intersect += 1
            elif object.kind == 'sign_T_intersection':
                sign_T += 1
            elif object.kind == 'sign_do_not_enter':
                sign_do_not_enter += 1
            elif object.kind == 'sign_duck_crossing':
                sign_duck += 1
            elif object.kind == 'sign_no_right_turn':
                sign_no_right_turn += 1
            elif object.kind == 'sign_no_left_turn':
                sign_no_left_turn += 1
            elif object.kind == 'sign_oneway_right':
                sign_oneway_right += 1
            elif object.kind == 'sign_oneway_left':
                sign_oneway_left += 1
            elif object.kind == 'sign_pedestrian':
                sign_pedestrian += 1
            elif object.kind == 'sign_stop':
                sign_stop += 1
            elif object.kind == 'sign_yield':
                sign_yield += 1
            elif object.kind == 'sign_t_light_ahead':
                sign_t_light_ahead += 1
            elif object.kind == 'sign_parking':
                parking += 1
    result += '{}{}: {} {}\n'.format(padding, _translate("MainWindow", "Number of T-shaped crossroads"), count_of_3way, _translate("MainWindow", "pcs"))
    result += '{}{}: {} {}\n'.format(padding, _translate("MainWindow", "Number of crossroads"), count_of_4way, _translate("MainWindow", "pcs"))
    result += '{}{}: {} {}\n'.format(padding, _translate("MainWindow", "Number of road"), count_of_str, _translate("MainWindow", "pcs"))
    result += '{}{}: {} {}\n'.format(padding, _translate("MainWindow", "Number of turn"), count_of_curve, _translate("MainWindow", "pcs"))
    result += '{}{}: {} {}\n'.format(padding, _translate("MainWindow", "Number of grass"), count_of_grass, _translate("MainWindow", "pcs"))
    result += '{}{}: {} {}\n'.format(padding, _translate("MainWindow", "Number of asphalt"), count_of_asphalt, _translate("MainWindow", "pcs"))
    result += '{}{}: {} {}\n'.format(padding, _translate("MainWindow", "Number of floor"), count_of_floor, _translate("MainWindow", "pcs"))

    result +='{}\n'.format(_translate("MainWindow", "Signs"))
    if sign_4_way:
        result += '{}{}: {} {}\n'.format(padding, _translate("MainWindow", "Crossroad"), sign_4_way, _translate("MainWindow", "pcs"))
    if sign_T:
        result += '{}{}: {} {}\n'.format(padding, _translate("MainWindow", "T-shaped crossroads"), sign_T, _translate("MainWindow", "pcs"))
    if sign_right_T_intersect:
        result += '{}{}: {} {}\n'.format(padding, _translate("MainWindow", "T-shaped right crossroads"), sign_right_T_intersect, _translate("MainWindow", "pcs"))
    if sign_left_T_intersect:
        result += '{}{}: {} {}\n'.format(padding, _translate("MainWindow", "T-shaped left crossroads"), sign_left_T_intersect, _translate("MainWindow", "pcs"))
    if sign_do_not_enter:
        result += '{}{}: {} {}\n'.format(padding, _translate("MainWindow", "Give away"), sign_do_not_enter, _translate("MainWindow", "pcs"))
    if sign_no_right_turn:
        result += '{}{}: {} {}\n'.format(padding, _translate("MainWindow", "No right turn"), sign_no_right_turn, _translate("MainWindow", "pcs"))
    if sign_no_left_turn:
        result += '{}{}: {} {}\n'.format(padding, _translate("MainWindow", "No left turn"), sign_no_left_turn, _translate("MainWindow", "pcs"))
    if sign_oneway_right:
        result += '{}{}: {} {}\n'.format(padding, _translate("MainWindow", "One-way street right"), sign_oneway_right, _translate("MainWindow", "pcs"))
    if sign_oneway_left:
        result += '{}{}: {} {}\n'.format(padding, _translate("MainWindow", "One-way street left"), sign_oneway_left, _translate("MainWindow", "pcs"))
    if sign_pedestrian:
        result += '{}{}: {} {}\n'.format(padding, _translate("MainWindow", "Pedestrian crossing"), sign_pedestrian, _translate("MainWindow", "pcs"))
    if sign_duck:
        result += '{}{}: {} {}\n'.format(padding, _translate("MainWindow", "Duck crossing"), sign_duck, _translate("MainWindow", "pcs"))
    if sign_stop:
        result += '{}{}: {} {}\n'.format(padding, _translate("MainWindow", "Stop"), sign_stop, _translate("MainWindow", "pcs"))
    if parking:
        result += '{}{}: {} {}\n'.format(padding, _translate("MainWindow", "Parking"), parking, _translate("MainWindow", "pcs"))
    if sign_yield:
        result += '{}{}: {} {}\n'.format(padding, _translate("MainWindow", "Give away"), sign_yield, _translate("MainWindow", "pcs"))
    if sign_t_light_ahead:
        result += '{}{}: {} {}\n'.format(padding, _translate("MainWindow", "Traffic light"), sign_t_light_ahead, _translate("MainWindow", "pcs"))
    return result


def materials_of_map(map, specifications):
    padding = '   '
    padding2 = padding + padding
    result = '{}\n   {}\n'.format(_translate("MainWindow", "Map materials"), _translate("MainWindow", "Tape"))

    white = 0
    yellow = 0
    red = 0

    for tile in np.array(map.get_tile_layer().data).flat:
        white += specifications[tile.kind]['white']
        yellow += specifications[tile.kind]['yellow']
        red += specifications[tile.kind]['red']

    if white:
        result += '{}{}: 4.8 x {} {}\n'.format(padding, _translate("MainWindow", "White"), white, _translate("MainWindow", "sm"))
    if yellow:
        result += '{}{}: 2.4 x {} {}\n'.format(padding, _translate("MainWindow", "Yellow"), yellow, _translate("MainWindow", "sm"))
    if red:
        result += '{}{}: 4.8 x {} {}\n'.format(padding, _translate("MainWindow", "Red"), red, _translate("MainWindow", "sm"))
    result += '{}\n'.format(_translate("MainWindow", "Blocks"))
    result += get_map_elements(map)
    result += get_map_objects(map)
    logger.debug("{}".format(result))
    return result


def specifications_of_map(map, specifications):
    road_length = 0
    result = "{}\n{}\n".format(_translate("MainWindow", "Map characteristics"), _translate("MainWindow", "Roads"))
    for tile in np.array(map.get_tile_layer().data).flat:
        road_length += specifications[tile.kind]['length']

    result += '      {}: {} {}\n'.format(_translate("MainWindow", "Road len"), road_length, _translate("MainWindow", "sm"))
    result += get_map_elements(map)
    logger.debug("{}".format(result))
    return result


def map_to_png(map_viewer: MapViewer, map_name):
    if '.png' not in map_name:
        map_name = map_name + '.png'
    tile_layer_data = map_viewer.map.get_tile_layer().data
    height = len(tile_layer_data)
    width = len(tile_layer_data[0])
    mergedImage = QtGui.QImage(width * map_viewer.map.gridSize, height * map_viewer.map.gridSize, QtGui.QImage.Format_RGB32)
    painter = QtGui.QPainter(mergedImage)
    transform = QtGui.QTransform()
    transform.translate(0, 0)
    painter.setTransform(transform, False)
    # Draw tile layer
    map_viewer.draw_tiles(tile_layer_data, painter, transform)
    # Draw objects
    for layer in map_viewer.map.get_object_layers(only_visible=True):
        map_viewer.draw_objects(layer.get_objects(), painter)
    painter.resetTransform()

    mergedImage.save(map_name, "png")
    painter.end()


def map_to_yaml(map, map_dir_path, lab_code=None):
    map_info = dict(map)
    for layer in map_info['layers']:
        if str(LayerType.TILES) in layer:
            layer['tile_size'] = map_info['tile_size']/100
        with open('{}/{}-{}.yaml'.format(map_dir_path, layer['type'], lab_code if lab_code else layer['name']), 'w') as map_file:
            yaml.safe_dump(layer['data'], map_file, default_flow_style=None)


def tiles_to_objects(tiles):
    default_fill_for_grid = {}

    # get size of grid
    size_x = max((tile['pose'][0] for tile in tiles)) + 1
    size_y = max((tile['pose'][1] for tile in tiles)) + 1
    size = (size_x, size_y)

    # create grid
    import numpy as np
    grid = np.full(size, fill_value=default_fill_for_grid)

    # fill grid by load tiles
    for tile in tiles:
        i, j = tile['pose'][:2]
        grid[i][j] = tile

    # fill empty tile in grid:
    for i, line in enumerate(grid):
        for j, tile in enumerate(line):
            line[j] = MapTile(**tile) if tile != default_fill_for_grid else MapTile(**{'pose': [i, j, 0], 'type': 'empty', 'angle': 'E'})
    return grid.tolist()


def map_objects_to_objects(map_objects):
    map_objects_array = []
    if not map_objects:
        return map_objects_array
    for map_object in map_objects:
        if 'optional' not in map_object:
            map_object['optional'] = False
        if 'static' not in map_object:
            map_object['static'] = True
        map_objects_array.append(map_object)
    return map_objects_array


last_data = None
last_map = None


def data_from_file(map_yaml):
    global last_data, last_map
    if last_map == map_yaml:
        return last_data
    try:
        with open(map_yaml, 'r') as file:
            last_data = yaml.safe_load(file)
        last_map = map_yaml
        return last_data
    except IOError:
        logger.debug("{}".format(_translate("MainWindow", "Could not open file!")))
        return None
