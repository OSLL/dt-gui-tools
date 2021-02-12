# -*- coding: utf-8 -*-
from .baseClass import PlacedObject
from .baseClass import BaseEditorClass
from random import randint

class MapBaseObject(PlacedObject):

    def __init__(self, **kwargs):
        PlacedObject.__init__(self, **kwargs)

    def __iter__(self):
        yield from {
            'pose': self.pose
        }.items()

    def get_editable_attrs(self):
        return {
            'pose': self.pose,
        }


class TagObject(MapBaseObject):

    def __init__(self, **kwargs):
        MapBaseObject.__init__(self, **kwargs)
        self.tag_id = kwargs['tag_id'] if 'tag_id' in kwargs else 0

    def __iter__(self):
        yield from {
            'tag_id': self.tag_id,
            'data':
            {
                'pose': {
                    'xyz': self.pose[:2],
                    #'slot': self.pose[2],
                    'rotate': self.pose[3:]
                }
            }
        }.items()

    def get_editable_attrs(self):
        return {
            'pose': self.pose,
            'tag_id': self.tag_id,
        }


class SignObject(TagObject):            # 1 layer
    pass

class GroundAprilTagObject(TagObject):  # 2 layer
    pass


class WatchTowerObject(MapBaseObject):  # 3 layer

    def __init__(self, **kwargs):
        MapBaseObject.__init__(self, **kwargs)
        self.hostname = kwargs["hostname"] if "hostname" in kwargs else "watchtower{}".format(randint(0, 10**3))  # TODO: How to init hostname?

    def __iter__(self):
        yield from {
            'hostname': self.hostname,
            'data':
            {
                'pose': {
                    'xyz': self.pose[:3],
                    'rotate': self.pose[3:]
                }
            }
        }.items()

    def get_editable_attrs(self):
        return {
            'pose': self.pose,
            'hostname': self.hostname
        }


class RegionObject(MapBaseObject):       # 4 layer NOT IMPLEMENTED
    pass


class ActorObject(MapBaseObject):       # 4 layer
    def __init__(self, **kwargs):
        MapBaseObject.__init__(self, **kwargs)
        self.kind = kwargs['kind']
        self.id = kwargs['ID'] if 'ID' in kwargs else '<ID_{}>'.format(self.kind)

    def __iter__(self):
        yield from {
            'kind': self.kind,
            'data':
            {
                'pose': {
                    'xyz': self.pose[:3],
                    'rotate': self.pose[3:]
                },
                'id': self.id
            }
        }.items()

    def get_editable_attrs(self):
        return {
            'pose': self.pose,
            'kind': self.kind,
            'id': self.id
        }


class DecorationObject(MapBaseObject):  # 6 layer
    def __init__(self, **kwargs):
        MapBaseObject.__init__(self, **kwargs)
        self.size = kwargs['size'] if 'size' in kwargs else 1
        self.mesh = kwargs['size'] if 'size' in kwargs else ['package', 'path']

    def __iter__(self):
        yield from {
            'pose': {
                    'xyz': self.pose[:3],
                    'rotate': self.pose[3:]
                },
            'mesh': self.mesh,
            'size': self.size
        }.items()

    def get_editable_attrs(self):
        return {
            'pose': self.pose,
            'mesh': self.mesh,
            'size': self.size
        }
