# -*- coding: utf-8 -*-
"""
Author  : NextPCG
"""
from .field import Field, FieldDesc
from .geo_texture import Texture


class TextureField(Field):
    """
    _value is a Texture
    """
    field_type_name = "paramType.Texture"
    support_param = False

    def __init__(self, value=None):
        self._value: Texture = value

    @classmethod
    def from_json(cls, json_object, input_name, field_desc: FieldDesc):
        if field_desc.work_path is None:
            raise Exception("TextureField from_json failed:work path need to be set, not allowed")
        value = Texture.create_from_json(json_object, field_desc.work_path, field_desc.io_mode, field_desc.raw_compress, input_name)
        return cls(value)

    def get_input(self):
        return self._value

    def get_output(self, json_field, field_desc: FieldDesc, data_field='Value Data', output_index=0):
        geo_index = 0
        self._value.to_json(geo_index, output_index, json_field, field_desc.io_mode, field_desc.work_path, field_desc.raw_compress)
