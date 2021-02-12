from json import dumps as json_dumps
from collections import defaultdict

from layers.base_layer import MapLayer


class TileLayer(MapLayer):

    def get_processed_layer_data(self):
        layer_data = {}
        for i, row in enumerate(self.data):
            for j, tile in enumerate(row):
                print('{}'.format(json_dumps([i, j, tile.k])))
                layer_data['{}'.format(json_dumps([i, j, tile.k]))] = dict(tile)
        return layer_data
        
    def get_objects(self):
        logger.info("Layer type {} doesn't support objects.")
        yield from ()
        

class TagLayer(MapLayer):
    #sign and tags
    def get_processed_layer_data(self):
        layer_data = defaultdict(list)
        for elem in self.data:
            elem = dict(elem)
            name_key = elem['tag_id']
            while name_key in layer_data:
                name_key = "_" + str(name_key) 
            layer_data[name_key] = elem['data']
        return dict(layer_data)


class WatchtowerLayer(MapLayer):
    
    def get_processed_layer_data(self):
        layer_data = {}
        for elem in self.data:
            elem = dict(elem)
            layer_data[elem['hostname']] = elem['data']
        return layer_data


class RegionLayer(MapLayer):
    
    def get_objects(self):
        logger.info("Layer type {} doesn't support objects.".format(self.type))
        yield from ()


class ActorLayer(MapLayer):

    def get_processed_layer_data(self):
        layer_data = defaultdict(list)
        for elem in self.data:
            elem = dict(elem)
            layer_data[elem['kind']].append(elem['data'])
        return dict(layer_data)

class DecorationLayer(MapLayer):
    pass