# -*- coding: utf-8 -*-
"""
Author  : NextPCG
"""

from .meta_helper import Singleton
from .const import *


class nextpcgmethod(staticmethod):
    def __init__(self, function):
        super(nextpcgmethod, self).__init__(function)


class DsonMetaInfo:
    """some wrapped meta info in dson file"""
    def __init__(self, cls_name:str, if_in_server:bool = False, dson_main_path:str = None):
        self.cls_name = cls_name
        self.if_in_server = if_in_server
        if(if_in_server == False):
            self.plugin_name = dson_main_path
        else:
            self.plugin_name = None           

    def to_json(self):
        json_data = {dson_meta_clsname_tag: self.cls_name, dson_meta_if_in_server_tag: self.if_in_server}
        if not self.if_in_server:
            json_data[dson_meta_plugin_name] = self.plugin_name
        return json_data

    @staticmethod
    def from_json(json_data):
        clsname = json_data[dson_meta_clsname_tag]
        if_in_server = True
        if dson_meta_if_in_server_tag in json_data:
            if_in_server = json_data[dson_meta_if_in_server_tag]
        dson_main_path = None
        if not if_in_server:
            dson_main_path = json_data[dson_meta_plugin_name]
        return DsonMetaInfo(clsname, if_in_server, dson_main_path)

    @staticmethod
    def from_dson(json_data):
        """from full dson file json"""
        for _, json_value in json_data.items():
            if dson_meta_field_tag in json_value:
                return DsonMetaInfo.from_json(json_value[dson_meta_field_tag])
        raise Exception("can't find dson meta info ")


class DsonManager(metaclass=Singleton):
    def __init__(self):
        self.dsonMap = {}


class DsonMeta(type):
    def __init__(cls, *args, **kwargs):
        assert hasattr(cls, 'label')
        DsonManager().dsonMap[cls.__name__] = cls
        super().__init__(*args, **kwargs)


class DsonBase(metaclass=DsonMeta):
    label = "pda"
    if_in_server = False # whether this class in NextPCG Server

    def __init__(self):
        pass
