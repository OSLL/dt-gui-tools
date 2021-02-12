# -*- coding: utf-8 -*-
from layers.base_layer import MapLayer
from layers.map_layer import TileLayer
from layers.layer_type import LayerType
import layers.layer_type as layer_relations
from tag_config import TRAFFIC_SIGN_TYPES
import logging

logger = logging.getLogger('root')


class DuckietownMap:
    name = None
    gridSize = 58.5

    def __init__(self, empty=False):
        self.layers = [TileLayer(LayerType.TILES, [[]])] if not empty else []

    def __iter__(self):
        yield from {
            'name': self.name,
            'tile_size': self.gridSize,
            'layers': [dict(layer) for layer in self.layers]
        }.items()

    # Getters

    def get_tile_layer(self):
        """
        Get tile layer's data (default name define by TILE_LAYER_NAME)
        :return: list(list)
        """
        return self.get_layer_by_type(LayerType.TILES)

    def get_item_layer(self):
        """
        Get item layer's data (default name define by ITEM_LAYER_NAME)
        If item layer doesn't exist, function create it
        :return: list
        """
        layer = self.get_layer_by_type(LayerType.ITEMS)
        if layer is None:  # if layer doesn't exist, layer = None
            layer = []
            self.add_layer_from_data(LayerType.ITEMS, layer)
        return layer

    def get_layer_by_type_name(self, name):
        """
        Get layer by name
        :param name: name of layer
        :return: list, if name doesn't exist, return None
        """
        for layer in self.layers:
            if str(layer.type) == name:
                return layer
        return None

    def get_layer_by_type(self, layer_type: LayerType):
        """
        Get layer by type
        :param layer_type: type of layer
        :return: list, if layer w/ type doesn't exist, return None
        """
        for layer in self.layers:
            if layer.type == layer_type:
                return layer
        return None

    def get_object_layers(self, only_visible=False):
        """
        Get layers with layer_type, that supports object placement.
        Layer types define by LAYER_TYPE_WITH_OBJECTS.
        If only_visible is True, return only visible layers
        :return: generator w/ layers
        """
        for layer in self.layers:
            if layer.type in layer_relations.LAYER_TYPE_WITH_OBJECTS and layer.visible:
                yield layer

    def get_objects_from_layers(self, only_visible=False):
        """
        Get all objects from layers in map
        If only_visible is True, return only objects from visible layers
        :return: generator w/ objects
        """
        for layer in self.get_object_layers(only_visible):
            for layer_object in layer.get_objects():
                yield layer_object

    # Setters

    def set_tile_layer(self, layer: list):
        """
        Set tile layer's data
        :param layer: list(list)
        :return: bool, return False if layer doesn't exist, else True
        """
        self.set_layer_data_by_type(LayerType.TILES, layer)

    def set_item_layer(self, layer: list):
        """
        Set item layer's data
        :param layer: list
        :return: bool, return False if layer doesn't exist, else True
        """
        self.set_layer_data_by_type(LayerType.ITEMS, layer)

    def set_layer_data_by_name(self, layer_name: str, layer_data: list):
        """
        Set layer's data by name
        :param layer_name: name of layer
        :param layer_data: list
        :return: bool, return False if layer doesn't exist, else True
        """
        layer = self.get_layer_by_type_name(layer_name)
        if layer:
            return self.set_layer_data_by_type(layer.type, layer_data)
        else:
            logger.info("Layer with name '{}' doesn't exist".format(layer_name))
            return False

    def set_layer_data_by_type(self, layer_type: LayerType, layer_data: list):
        """
        Set layer's data by name
        :param layer_type: type of layer
        :param layer_data: list
        :return: bool, return False if layer doesn't exist, else True
        """
        layer = self.get_layer_by_type(layer_type)
        if layer:
            layer.data = layer_data
            return True
        else:
            logger.info("Layer with type '{}' doesn't exist".format(layer_type))
            return False

    def set_layer(self, new_layer: MapLayer):
        for i, layer in enumerate(self.layers):
            if layer.type == new_layer.type:
                self.layers[i] = new_layer
                return True
        logger.info("Layer with type '{}' doesn't exists. Can't set new layer".format(new_layer.type))

    # Creating layer

    def add_layer_from_data(self, layer_type: LayerType, layer_data=None, layer_name=''):
        """
        Add layer to map from layer_type and layer_data
        :param layer_type: LayerType
        :param layer_data: list
        :param layer_name: str
        :return: bool, return False, if layer with such LayerType already exists, else True
        """
        if self.get_layer_by_type(layer_type):
            logger.info("Layer with type '{}' already exists.\nTo set new layer data use "
                        "set_layer_data/set_layer_data_by_type.\nTo set new layer name use "
                        "set_layer_name/set_layer_name_by_type".format(layer_type))
            return False
        else:
            layer_class = layer_type.get_layer_class()
            return self.add_layer(layer_class(layer_type, layer_data if layer_data else [], layer_name))

    def add_layer(self, layer: MapLayer):
        """
        Add layer to map
        :param layer: MapLayer
        :return: bool, return False, if layer with such LayerType already exists, else True
        """
        if self.get_layer_by_type(layer.type):
            logger.info("Layer with type '{}' already exists.\nTo set new layer data use "
                        "set_layer_data/set_layer_data_by_type.\nTo set new layer name use "
                        "set_layer_name/set_layer_name_by_type".format(layer.type))
            return False
        else:
            self.layers.append(layer)
            return True

    # Adding elem to layers

    def add_item(self, item):
        """
        Add item to item layer (default name define by ITEM_LAYER_NAME)
        :param item: MapObject. Note: after adding specific layers, it can change
        :return: bool (looks like it always True)
        """
        return self.add_elem_to_layer_by_type(LayerType.ITEMS, item)

    def add_elem_to_layer(self, layer_name: str, elem):
        """
        Add elem to layer by name
        (Doesn't add elements to tile_layer due to different structure)
        :param layer_name: name of layer
        :param elem: MapObject. Note: after adding specific layers, it can change
        :return: bool, return False if layer doesn't exist, else True
        """
        layer = self.get_layer_by_type_name(layer_name).type
        if layer is not None:
            return self.add_elem_to_layer_by_type(layer.type, elem)
        else:
            logger.info("Layer with name '{}' doesn't exist".format(layer_name))
            return False

    def add_elem_to_layer_by_type(self, layer_type: LayerType, elem):
        """
        Add elem to layer by type
        (Doesn't add elements to tile_layer due to different structure)
        :param layer_type: type of layer
        :param elem: MapObject. Note: after adding specific layers, it can change
        :return: bool, return False if layer doesn't exist, else True
        """
        if layer_type == LayerType.TILES:
            logger.warning("Don't use this method for tile layer.")
            return False
        layer = self.get_layer_by_type(layer_type)
        if layer is not None:  # layer can exist, but be empty. get_layer_by_type_name/get_layer_by_type return None, if layer doesn't exist
            layer.add_elem(elem)
            return True
        else:
            logger.info("Layer with type '{}' doesn't exist".format(layer_type))
            return False

    def add_objects_to_map(self, objects, info_about_objects):
        for map_object in objects:
            object_type = info_about_objects[map_object['kind']]['type']
            layer_type = layer_relations.get_layer_type_by_object_type(object_type)
            if layer_type == LayerType.TRAFFIC_SIGNS:
                tag_ids = TRAFFIC_SIGN_TYPES[map_object['kind']]
                map_object['tag_id'] = tag_ids[0] if 'tag_id' not in map_object and tag_ids else 0
                print(tag_ids, dict(map_object))
            map_object = LayerType.create_layer_object(object_type, map_object)
            if not self.get_layer_by_type(layer_type):
                self.add_layer_from_data(layer_type, [map_object])
            else:
                self.add_elem_to_layer_by_type(layer_type, map_object)
    
    def add_objects_to_layer(self, objects, layer_type, layer_name=''):
        objects_to_layer = []
        obj_class = layer_relations.get_class_by_layer_type(layer_type)
        # adding tile layer
        if layer_type == LayerType.TILES:
            for layer_object in objects:
                new_obj = []
                for tile in layer_object:
                    new_obj.append(obj_class(tile))
                objects_to_layer.append(new_obj)
            self.add_layer_from_data(layer_type, objects_to_layer, layer_name)
        else:
            layer = self.get_layer_by_type(layer_type)
            for layer_object in objects:

                objects_to_layer.append(obj_class(layer_object))
            layer = self.get_layer_by_type(layer_type)
            if layer:
                layer.add_elem(objects_to_layer)
            else:
                self.add_layer_from_data(layer_type, objects_to_layer, layer_name)

    def clear_objects_layers(self):
        self.layers = [self.get_layer_by_type(LayerType.TILES)]
   