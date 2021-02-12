from enum import Enum
from collections import namedtuple

from classes.mapTile import MapTile
from classes.mapObjects import MapBaseObject, SignObject, GroundAprilTagObject, WatchTowerObject, RegionObject, ActorObject, DecorationObject
from layers.map_layer import TileLayer, TagLayer, WatchtowerLayer, RegionLayer, ActorLayer, DecorationLayer

LayerInfo = namedtuple('LayerInfo', ['type', 'obj_type', 'obj_class', 'layer_class'])


class LayerType(Enum):
    TILES = LayerInfo('0-tiles', None, MapTile, TileLayer)
    TRAFFIC_SIGNS = LayerInfo('1-signs', 'sign', SignObject, TagLayer)
    GROUND_APRILTAG = LayerInfo('2-groundtags', 'apriltag', GroundAprilTagObject, TagLayer)
    WATCHTOWERS = LayerInfo('3-watchtowers', 'watchtower', WatchTowerObject, WatchtowerLayer)
    REGIONS = LayerInfo('4-regions', None, RegionObject, RegionLayer)
    ACTORS = LayerInfo('5-actors', 'actor', ActorObject, ActorLayer)
    DECORATIONS = LayerInfo('6-decorations', 'decoration', DecorationObject, DecorationLayer)

    def __str__(self):
        return self.value.type

    def get_obj_class(self):
        return self.value.obj_class

    def get_layer_class(self):
        return self.value.layer_class

    @staticmethod
    def create_layer_object(object_type, object_data):
        return get_class_by_object_type(object_type)(**object_data)


def get_class_by_object_type(object_type):
    """
    Get map object class from classes.mapObjects for object_type
    If object_type doesn't exist, return MapBaseObject
    :param object_type: type of object
    :return: class of map object
    """
    for layer_type_info in list(LayerType):
        layer_type, obj_type, obj_class, *_ = layer_type_info.value
        if object_type == obj_type:
            return obj_class
    return LayerType.ITEMS.get_obj_class()


def get_class_by_layer_type(layer_type):
    """
    Get map object class from classes.mapObjects for layer_type
    :param layer_type: LayerType
    :return: class of map object
    """
    return layer_type.get_obj_class()


def get_layer_type_by_object_type(object_type):
    """
    Get layer type by object type (help know what layer type need for this object_type)
    If object_type doesn't exist, return LayerType.ITEMS
    :param object_type: type of object
    :return: LayerType
    """
    for layer_type_info in list(LayerType):
        layer_type, obj_type, obj_class, *_ = layer_type_info.value
        if object_type == obj_type:
            return layer_type_info
    return LayerType.ITEMS


def get_layer_type_by_value(type_value):
    for layer_type in LayerType: 
        if type_value == layer_type.value:
            return layer_type


LAYER_TYPE_WITH_OBJECTS = (LayerType.TRAFFIC_SIGNS, LayerType.GROUND_APRILTAG, LayerType.WATCHTOWERS, LayerType.ACTORS, LayerType.DECORATIONS)

