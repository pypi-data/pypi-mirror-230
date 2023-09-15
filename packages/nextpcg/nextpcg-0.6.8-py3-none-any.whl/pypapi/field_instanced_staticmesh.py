# -*- coding: utf-8 -*-
"""
Author  : NextPCG
"""

from .field import Field, FieldCategory, FieldDesc
from .geo_instanced_staticmesh import InstancedStaticMesh


class InstancedStaticMeshField(Field):
    """
    _value is a InstanceStaticMesh
    """
    field_type_name = "paramType.InstancedStaticMesh"
    support_param = False

    def __init__(self, value):
        self._value = value

    @classmethod
    def from_json(cls, json_object, input_name, field_desc:FieldDesc):
        if field_desc.work_path is None:
            raise Exception("HeightFieldField from_json failed:work path need to be set, not allowed")
        value = InstancedStaticMesh.create_from_json(json_object, field_desc.work_path, field_desc.io_mode, input_name)
        return InstancedStaticMeshField(value)

    def get_input(self):
        return self._value

    def get_output(self, json_field, field_desc, data_field='Value Data', output_index=0):
        geo_index = 0
        self._value.to_json(geo_index, output_index, json_field, field_desc.io_mode, field_desc.work_path)
