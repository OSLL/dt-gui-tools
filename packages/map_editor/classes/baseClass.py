# -*- coding: utf-8 -*-

class BaseEditorClass:
    def __init__(self,  **kwargs):
        pass

    def __iter__(self):
        raise NotImplementedError("Subclasses should implement __iter__")


class PlacedObject(BaseEditorClass):

    def __init__(self, **kwargs):
        BaseEditorClass.__init__(self,  **kwargs)
        position = list(kwargs['pose'])
        position.extend([0.0]*4) if len(position) == 2 else None    # support pose = [x, y]
        self.pose = position
        if 'kind' in kwargs:
            self.kind = kwargs['kind']

    def __iter__(self):
        raise NotImplementedError("Subclasses should implement __iter__")

    def add_to_pose_xy(self, x=None, y=None):
        if x:
            self.pose[0] += x
        if y:
            self.pose[1] += y

    def get_pose_xy(self):
        return self.pose[:2]

    def set_pose_xy(self, x=None, y=None):
        if x:
            self.pose[0] = x
        if y:
            self.pose[1] = y

    def get_editable_attrs(self):
        raise NotImplementedError("Subclasses should implement get_editable_attrs")