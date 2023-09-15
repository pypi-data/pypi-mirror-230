# -*- coding: utf-8 -*-
"""
Author  : NextPCG
"""

from .field import Field, FieldCategory, FieldDesc
from .geo_heightfield import HeightField
from typing import List


class HeightFieldField(Field):
    """
    _value is list of HeightField
    """
    field_type_name = "paramType.HeightField"
    support_param = False

    def __init__(self, value=None):
        self._value: List[HeightField] = value

    @classmethod
    def from_json(cls, json_object, input_name, field_desc):
        if field_desc.work_path is None:
            raise Exception("HeightFieldField from_json failed:work path need to be set, not allowed")
        value = []
        for editing_layer_key, editing_layer_val in json_object.items():
            if 'EditingLayer_' in editing_layer_key:
                heightfield = HeightField.create_from_json(json_object, editing_layer_val, field_desc.work_path, field_desc.io_mode, field_desc.raw_compress)
                value.append(heightfield)
        return cls(value)

    def get_input(self):
        return self._value

    def get_output(self, json_field, field_desc: FieldDesc, data_field='Value Data', output_index=0):
        geo_index = 0
        for heightfield in self._value:
            num = heightfield.to_json(geo_index, output_index, json_field, field_desc.io_mode, field_desc.work_path, field_desc.raw_compress)
            geo_index += num

