# -*- coding: utf-8 -*-

from .baseClass import BaseEditorClass


class MapTile(BaseEditorClass):
    rotation_val = {
        'to_str': {0: 'E', 90: 'S', 180: 'W', 270: 'N'},
        'to_int': {'E': 0, 'S': 90, 'W': 180, 'N': 270}
    }
    no_rotation_tile = ('empty', 'asphalt', 'grass', 'floor', '4way')

    def __init__(self, **kwargs):
        BaseEditorClass.__init__(self, **kwargs)
        self.type = kwargs['type']
        self.angle = kwargs['angle'] if 'angle' in kwargs else 'E'
        self.k = kwargs['pose'][2] if 'pose' in kwargs else 0

        # for editor supporting
        self.kind = self.type
        self.rotation = self.angle_to_int(self.angle)

    def __iter__(self):
        yield from {
            'type': self.kind,
            'angle': self.angle
        }.items()

    def __str__(self):
        return '{}/{}'.format(self.kind, self.angle_to_str(self.angle))

    def __repr__(self):
        return self.__str__()

    def angle_to_str(self, angle: int):
        if self.type not in self.no_rotation_tile:
            return self.rotation_val['to_str'][angle]
        else:
            return 'E'

    def angle_to_int(self, angle: str):
        if self.type not in self.no_rotation_tile:
            return self.rotation_val['to_int'][angle]
        else:
            return 0

    def get_rotation(self):
        return self.rotation

    def set_rotation(self, rotation):
        self.rotation = rotation
        self.angle = self.angle_to_str(rotation)

