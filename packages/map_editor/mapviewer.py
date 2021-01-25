# -*- coding: utf-8 -*-
import logging
from typing import Tuple

from PyQt5.QtWidgets import QGraphicsView
from PyQt5 import QtCore, QtGui, QtWidgets
from duckietown_world.structure.objects import Tile, _Tile

from map import DuckietownMap
from utils import get_list_dir_with_path
from classes.mapObjects import MapBaseObject
import numpy as np
import duckietown_world.structure as st
from DTWorld import get_dt_world
import os

logger = logging.getLogger('root')

TILES_DIR_PATH = './img/tiles'
OBJECT_DIR_PATHS = ['./img/signs',
                    './img/apriltags',
                    './img/objects']

DELTA_EUCLIDEAN_DISTANCE = .15


# TILE_SIZE = 0.585


class MapViewer(QGraphicsView, QtWidgets.QWidget):
    map = None
    tileSprites = {'empty': QtGui.QImage()}
    objects = {'stop': QtGui.QImage()}
    offsetX = 0
    offsetY = 0
    sc = 1
    rmbPressed = False
    lmbPressed = False
    drag_mode = False
    drag_obj = None
    rmbPrevPos = [0, 0]
    mouseStartX, mouseStartY = 0, 0
    mouseCurX, mouseCurY = 0, 0
    tile_size = 0.585
    #  Stores the top left and bottom right coordinates of the selected area (including zero size areas) as array indexes
    #  If the selection is outside the array to the left, contains -1
    #  If the selection is outside the array to the right - width / height
    tileSelection = [0] * 4
    selectionChanged = QtCore.pyqtSignal()
    editObjectChanged = QtCore.pyqtSignal(tuple)
    lmbClicked = QtCore.pyqtSignal(int, int)  # click coordinates as an index of the clicked tile

    def __init__(self):
        QGraphicsView.__init__(self)
        map_name = os.path.abspath("maps/tm1")
        # print(map_name)
        self.dm = get_dt_world(map_name)
        self.setScene(QtWidgets.QGraphicsScene())
        # load tiles
        for filename, file_path in get_list_dir_with_path(TILES_DIR_PATH):
            tile_name = filename.split('.')[0]
            self.tileSprites[tile_name] = QtGui.QImage()
            self.tileSprites[tile_name].load(file_path)
        # load objects
        for dir_path in OBJECT_DIR_PATHS:
            for filename, file_path in get_list_dir_with_path(dir_path):
                object_name = filename.split('.')[0]
                self.objects[object_name] = QtGui.QImage()
                self.objects[object_name].load(file_path)

    def setMap(self, tiles: DuckietownMap):
        self.map = tiles
        self.raw_selection = [0] * 4
        self.tileSelection = [0] * 4
        self.scene().update()

    def get_x_from_view(self, x_view: float) -> float:
        logger.debug((x_view - self.offsetX) / self.sc / self.map.gridSize * self.tile_size)
        return (x_view - self.offsetX) / self.sc / self.map.gridSize * self.tile_size

    def get_y_from_view(self, y_view: float) -> float:
        logger.debug((len(self.dm.tiles.only_tiles()[0]) - (y_view - self.offsetY) / self.sc / self.map.gridSize) \
                     * self.tile_size)
        return (len(self.dm.tiles.only_tiles()[0]) - (y_view - self.offsetY) / self.sc / self.map.gridSize) \
               * self.tile_size

    def get_x_to_view(self, x_real: float) -> float:
        return (x_real + 0) * self.sc * self.map.gridSize / self.tile_size

    def get_y_to_view(self, y_real: float) -> float:
        return ((len(self.dm.tiles.only_tiles()[0]) - y_real / self.tile_size) + 0) * self.sc * self.map.gridSize

    def wheelEvent(self, event: QtGui.QWheelEvent) -> None:
        sf = 2 ** (event.angleDelta().y() / 240)
        if (self.sc < 0.05 and sf < 1) or (self.sc > 100 and sf > 1):
            return
        self.sc *= sf
        self.scene().update()

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        self.drag_mode = False
        self.drag_obj = None
        if event.button() == QtCore.Qt.LeftButton:
            self.lmbPressed = False
            if int((self.mouseStartX - self.offsetX) / self.sc * self.map.gridSize) == int(
                    (self.mouseCurX - self.offsetX) / self.sc * self.map.gridSize) and int(
                (self.mouseStartY - self.offsetY) / self.sc * self.map.gridSize) == int(
                (self.mouseCurY - self.offsetY) / self.sc * self.map.gridSize):
                self.lmbClicked.emit(int((self.mouseStartX - self.offsetX) / self.sc * self.map.gridSize),
                                     int((self.mouseStartY - self.offsetY) / self.sc * self.map.gridSize))

            self.raw_selection = [
                ((min(self.mouseStartX, self.mouseCurX) - self.offsetX) / self.sc
                 ) / self.map.gridSize,
                self.get_y_from_view(min(self.mouseStartY, self.mouseCurY)) / self.tile_size,
                ((max(self.mouseStartX, self.mouseCurX) - self.offsetX) / self.sc) / self.map.gridSize,
                self.get_y_from_view(max(self.mouseStartY, self.mouseCurY)) / self.tile_size
            ]

            if self.map.get_tile_layer().visible:
                self.tileSelection = [
                    int(v)  # + (1 if i > 1 else 0)
                    for i, v in enumerate(self.raw_selection)
                ]
            self.selectionChanged.emit()
        else:
            self.rmbPressed = False
        self.scene().update()

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        x, y = event.x(), event.y()
        x_map = self.get_x_from_view(x)
        y_map = self.get_y_from_view(y)
        if event.buttons() == QtCore.Qt.LeftButton:
            drag_obj, _ = self.find_object(x_map, y_map)
            print('before drag,', x_map, y_map)
            if drag_obj:
                print(drag_obj)
                self.drag_obj = drag_obj
                self.drag_mode = True
                return
        if event.buttons() == QtCore.Qt.RightButton:
            obj, (name, tp) = self.find_object(x_map, y_map)
            if obj:
                self.editObjectChanged.emit((obj, name))
            else:
                # if press event is not near with any object
                self.rmbPrevPos = [x, y]
                self.rmbPressed = True
        elif event.buttons() == QtCore.Qt.LeftButton:
            self.lmbPressed = True
            self.mouseCurX = self.mouseStartX = x
            self.mouseCurY = self.mouseStartY = y

    def find_object(self, x, y) -> Tuple:
        event_x = np.array((x, y))
        for frame_name, frame in self.dm.frames:
            obj_x = frame.pose.x
            obj_y = frame.pose.y
            obj_array = np.array((obj_x, obj_y))
            if np.linalg.norm(obj_array - event_x) < DELTA_EUCLIDEAN_DISTANCE:
                logger.debug('Found frame: {}'.format(frame))
                try:
                    name, _ = frame_name
                    print('Tile of frame-{}:'.format(name), self.dm.tiles[name])
                except:
                    pass
                return frame, frame_name
        return None, None

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        x, y = event.x(), event.y()
        x_map = self.get_x_from_view(x)
        y_map = self.get_y_from_view(y)
        if self.drag_mode:
            self.drag_obj.pose.x = x_map
            self.drag_obj.pose.y = y_map
            self.scene().update()
        elif self.rmbPressed:
            self.offsetX += event.x() - self.rmbPrevPos[0]
            self.offsetY += event.y() - self.rmbPrevPos[1]
            self.rmbPrevPos = [event.x(), event.y()]
            self.scene().update()
        elif self.lmbPressed:
            self.mouseCurX = event.x()
            self.mouseCurY = event.y()
            self.scene().update()

    def drawBackground(self, painter: QtGui.QPainter, rect: QtCore.QRectF):
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        painter.resetTransform()
        painter.fillRect(0, 0, self.size().width(), self.size().height(), QtGui.QColor('darkGray'))
        global_transform = QtGui.QTransform()
        global_transform.translate(self.offsetX, self.offsetY)
        painter.setTransform(global_transform, False)

        # Draw tile layer
        tile_layer = self.map.get_tile_layer()
        # print(self.dm.tiles)
        # print(self.dm.tile_maps)
        # print(self.dm.citizens)
        if tile_layer and tile_layer.visible:
            self.draw_tiles(tile_layer.data, painter, global_transform)
        # painter.scale(self.sc, self.sc)
        # Draw layer w/ objects
        self.draw_objects(painter)

        # for layer in self.map.get_object_layers(only_visible=True):
        #    self.draw_objects(layer.get_objects(), painter)

        painter.resetTransform()
        painter.setPen(QtGui.QColor('black'))
        if self.lmbPressed:
            painter.drawRect(0 + self.mouseStartX, 0 + self.mouseStartY
                             , self.mouseCurX - self.mouseStartX, self.mouseCurY - self.mouseStartY)

    def draw_tiles(self, layer_data, painter, global_transform):
        rot_val = {'E': 0, 'S': 90, 'W': 180, 'N': 270, None: 0}
        tiles = self.dm.tiles.only_tiles()
        for i in range(len(tiles)):
            for j in range(len(tiles[0])):
                tile = tiles[i][j]
                orientation = tile.orientation
                painter.scale(self.sc, self.sc)
                painter.translate(tile.i * self.map.gridSize, (len(tiles[0]) - 1 - tile.j) * self.map.gridSize)
                painter.rotate(rot_val[orientation])
                if orientation == "S":
                    painter.translate(0, -self.map.gridSize)
                elif orientation == "N":
                    painter.translate(-self.map.gridSize, 0)
                elif orientation == "W":
                    painter.translate(-self.map.gridSize, -self.map.gridSize)

                painter.drawImage(QtCore.QRectF(0, 0, self.map.gridSize, self.map.gridSize),
                                  self.tileSprites[tile.type])
                # print(self.tileSelection)
                if self.is_selected_tile(tile):
                    painter.setPen(QtGui.QColor('green'))
                    painter.drawRect(QtCore.QRectF(1, 1, self.map.gridSize - 1, self.map.gridSize - 1))
                else:
                    painter.setPen(QtGui.QColor('white'))
                    painter.drawRect(QtCore.QRectF(0, 0, self.map.gridSize, self.map.gridSize))
                if tile.j == 0 and tile.i == 0:
                    painter.setPen(QtGui.QColor('blue'))
                    painter.drawRect(QtCore.QRectF(1, 1, self.map.gridSize - 1, self.map.gridSize - 1))
                painter.setTransform(global_transform, False)

    def is_selected_tile(self, tile: _Tile) -> bool:
        return self.tileSelection[0] <= tile.i <= self.tileSelection[2] and self.tileSelection[3] <= tile.j <= \
               self.tileSelection[1]

    def draw_objects(self, painter):
        width, height = self.map.gridSize * self.sc / 2, self.map.gridSize * self.sc / 2
        self.draw_watchtowers(width, height, painter)
        self.draw_citizens(width, height, painter)
        self.draw_traffic_signs(width, height, painter)
        self.draw_groundtags(width, height, painter)

    def draw_citizens(self, width, height, painter):
        self.raw_draw_objects(width, height, painter, self.dm.citizens, "duckie")

    def draw_watchtowers(self, width, height, painter):
        if self.dm.watchtowers is not None:
            self.raw_draw_objects(width, height, painter, self.dm.watchtowers, "watchtower")

    def draw_traffic_signs(self, width, height, painter):
        for info, object in self.dm.trafficsigns:
            obj_name, obj_type = info
            frame_obj = self.dm.frames[obj_name]
            x, y = 0, 0
            frame_of_pose = frame_obj
            while frame_of_pose:
                x += frame_of_pose.pose.x
                y += frame_of_pose.pose.y
                frame_of_pose = self.dm.frames[frame_of_pose.relative_to]
            # - width / 2
            # - height / 2
            x, y = self.get_x_to_view(x), self.get_y_to_view(y)
            painter.drawImage(
                QtCore.QRectF(x - width / 2,
                              y - height / 2,
                              width, height),
                self.objects[object.type])

    def draw_groundtags(self, width, height, painter):
        self.raw_draw_objects(width, height, painter, self.dm.groundtags, "apriltag")

    def raw_draw_objects(self, width, height, painter, arr_objects, type_name):
        for info, object in arr_objects:
            obj_name, obj_type = info
            frame_obj = self.dm.frames[obj_name]
            x, y = 0, 0
            frame_of_pose = frame_obj
            while frame_of_pose:
                x += frame_of_pose.pose.x
                y += frame_of_pose.pose.y
                frame_of_pose = self.dm.frames[frame_of_pose.relative_to]
            # - width / 2
            # - height / 2
            x, y = self.get_x_to_view(x), self.get_y_to_view(y)
            painter.drawImage(
                QtCore.QRectF(x - width / 2,
                              y - height / 2,
                              width, height),
                self.objects[type_name])

        # for layer_object in layer_data:
        #
        #    painter.drawImage(
        #        QtCore.QRectF(self.map.gridSize * self.sc * layer_object.position[0] - width / 2,
        #                      self.map.gridSize * self.sc * layer_object.position[1] - height / 2,
        #                      width, height),
        #        self.objects[layer_object.kind]) if layer_object.kind in self.objects else None
