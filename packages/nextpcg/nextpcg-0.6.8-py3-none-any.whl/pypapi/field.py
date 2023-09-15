# -*- coding: utf-8 -*-
"""
Author  : NextPCG
"""

import json
import os
import time
from typing import Dict, List, Tuple, Any
from inspect import signature, Signature, Parameter
import logging
from abc import ABCMeta, abstractmethod
from enum import Enum
from .meta_helper import Singleton

"""note:
io_mode:
0: server_text (like houdini_text)
1: houdini_text (support)
2: houdini_binary (support)
3: houdini_hdk (not support)
 """


class FieldDesc:
    """
    helper struct used when create field or get outputs from field
    """

    def __init__(self, work_path, io_mode=1, raw_compress=False) -> None:
        self.work_path: str = work_path
        self.raw_compress: bool = raw_compress
        self.io_mode: int = io_mode


def unique_name():
    n = 1
    while True:
        yield n
        n += 1
        if n > 10000:
            n = 1


unique_name_generator = unique_name()

'''
FieldManager   
'''


class FieldManager(metaclass=Singleton):
    def __init__(self):
        self.fieldMap = {}  # map from field_type_name(str) to actual Field

    def create_field(self, json_object, input_name, field_desc: FieldDesc):
        """create a Field

        Args:
            json_object(Dict)
            work_path(str)
        Return:
            Field
            """
        # try:
        assert "If List" in json_object
        if json_object['If List']:
            return ListField.from_json(json_object, input_name, field_desc)
        else:
            return self.fieldMap[json_object['Type']].from_json(json_object, input_name, field_desc)
        # except Exception as e:
        #     logging.exception("get_input failed, json_object:" + str(json_object))

    def __getitem__(self, item):
        return self.fieldMap[item]


'''
define Field
'''

BOOL_TYPE = 'paramType.Bool'
INT_TYPE = 'paramType.Int'
INT2_TYPE = 'paramType.Int2'
INT3_TYPE = 'paramType.Int3'
INT4_TYPE = 'paramType.Int4'
FLOAT_TYPE = 'paramType.Float'
FLOAT2_TYPE = 'paramType.Float2'
FLOAT3_TYPE = 'paramType.Float3'
FLOAT4_TYPE = 'paramType.Float4'
STRING_TYPE = 'paramType.String'
JSON_TYPE = 'paramType.Json'
FILE_TYPE = 'paramType.File'
LIST_TYPE = 'paramType.List'


class FieldCategory(Enum):
    Input = 0
    Param = 1
    Output = 2


class FieldMeta(type):
    def __init__(cls, *args, **kwargs):
        assert hasattr(cls, 'field_type_name')
        FieldManager().fieldMap[cls.field_type_name] = cls
        super().__init__(*args, **kwargs)


"""some notes about Field
1. field_type_name will be registered in FieldManager. So FiledManager Can create Field according to 'Type' field in json object
2. create_json_field(): for supporting generate json from function's signature
3. from_json : for creating field from json field in Inputs or Params
4. get_input: functions use this method to get actual value to impl_function
5. get_output: fill the 'Value Data' hole in json_field
"""


class Field(metaclass=FieldMeta):
    field_type_name = ""
    if_list = False
    support_param = True  # if this field can be a param(with default value)

    @classmethod
    def create_json_field(cls, field_category=FieldCategory.Input, name: str = None):
        """ create a json object
        """
        """get json format field"""
        field = {'Type': cls.field_type_name, 'If List': cls.if_list, 'FieldCategory': field_category.name}
        if name is not None:
            field["Label"] = name
        return field

    def __init__(self, value=None):
        self._value = value

    @classmethod
    def from_json(cls, json_object, input_name, field_desc: FieldDesc):
        """
        Args:
            json_object: the json field describe this field type in json(dson) file
        """
        return cls(json_object['Value Data'])

    def get_input(self):
        """ pass input to impl function"""
        self.type_assert()
        return self._value

    def type_assert(self):
        pass

    def get_output(self, json_field, field_desc: FieldDesc, data_field='Value Data', output_index=0):
        json_field[data_field] = self._value

    @classmethod
    def get_param_default(cls, json_object, default_value):
        """fill default value to json field"""
        json_object["Default Value"] = default_value


# base class for those who want to support list field
class ListSubFieldBase:
    @classmethod
    def list_from_json_value(cls, json_value, work_path=None):
        return json_value

    @classmethod
    def list_to_json_value(cls, val, work_path=None):
        return val


class Bool(Field):
    field_type_name = BOOL_TYPE

    @classmethod
    def from_json(cls, json_object, input_name, field_desc: FieldDesc):
        return cls(bool(json_object['Value Data'][0]))

    def get_output(self, json_field, field_desc: FieldDesc, data_field='Value Data', output_index=0):
        # json_field[data_field] = [str(self._value)]
        json_field[data_field] = [self._value]


class Int(Field, ListSubFieldBase):
    field_type_name = INT_TYPE

    def type_assert(self):
        assert isinstance(self._value, int)

    @classmethod
    def from_json(cls, json_object, input_name, field_desc: FieldDesc):
        return cls(int(json_object['Value Data'][0]))

    def get_output(self, json_field, field_desc: FieldDesc, data_field='Value Data', output_index=0):
        # json_field[data_field] = [str(self._value)]
        json_field[data_field] = [self._value]

    @classmethod
    def get_param_default(cls, json_object, default_value):
        json_object["Default Value"] = [default_value]


class Int2(Field, ListSubFieldBase):
    field_type_name = INT2_TYPE

    def type_assert(self):
        assert isinstance(self._value, tuple) or isinstance(self._value, list)
        if len(self._value) != 2:
            raise Exception("value is not int2: " + str(self._value))

    @classmethod
    def from_json(cls, json_object, input_name, field_desc: FieldDesc):
        return cls(list(map(lambda a: int(a), json_object['Value Data'])))

    def get_output(self, json_field, field_desc: FieldDesc, data_field='Value Data', output_index=0):
        # json_field[data_field] = list(map(lambda a: str(a), self._value))
        json_field[data_field] = self._value


class Int3(Int2):
    field_type_name = INT3_TYPE

    def type_assert(self):
        assert isinstance(self._value, tuple) or isinstance(self._value, list)
        if len(self._value) != 3:
            raise Exception("value is not int3: " + str(self._value))


class Int4(Int2):
    field_type_name = INT4_TYPE

    def type_assert(self):
        assert isinstance(self._value, tuple) or isinstance(self._value, list)
        if len(self._value) != 4:
            raise Exception("value is not int4: " + str(self._value))


class Float(Field):
    field_type_name = FLOAT_TYPE

    def type_assert(self):
        assert isinstance(self._value, float)

    @classmethod
    def from_json(cls, json_object, input_name, field_desc: FieldDesc):
        return cls(float(json_object['Value Data'][0]))

    def get_output(self, json_field, field_desc: FieldDesc, data_field='Value Data', output_index=0):
        # json_field[data_field] = [str(self._value)]
        json_field[data_field] = [self._value]

    @classmethod
    def get_param_default(cls, json_object, default_value):
        assert isinstance(default_value, float)
        json_object['Default Value'] = [default_value]


class Float2(Field, ListSubFieldBase):
    field_type_name = FLOAT2_TYPE

    def type_assert(self):
        assert isinstance(self._value, tuple) or isinstance(self._value, list)
        if len(self._value) != 2:
            raise Exception("value is not float2: " + str(self._value))

    @classmethod
    def from_json(cls, json_object, input_name, field_desc: FieldDesc):
        # return cls(list(map(lambda a: float(a), json_object['Value Data'])))
        return cls(json_object['Value Data'])

    def get_output(self, json_field, field_desc: FieldDesc, data_field='Value Data', output_index=0):
        # json_field['Value Data'] = list(map(lambda a: str(a), self._value))
        json_field[data_field] = self._value


class Float3(Float2, ListSubFieldBase):
    field_type_name = FLOAT3_TYPE

    def type_assert(self):
        assert isinstance(self._value, tuple) or isinstance(self._value, list)
        if len(self._value) != 3:
            raise Exception("value is not float2:" + str(self._value))


class Float4(Float2):
    field_type_name = FLOAT4_TYPE

    def type_assert(self):
        assert isinstance(self._value, tuple) or isinstance(self._value, list)
        if len(self._value) != 4:
            raise Exception("value is not float2:" + str(self._value))


class String(Field, ListSubFieldBase):
    field_type_name = STRING_TYPE

    def type_assert(self):
        assert isinstance(self._value, str)

    @classmethod
    def create_json_field(cls, field_category=FieldCategory.Input, name: str = None):
        field = super().create_json_field(field_category, name)
        field["String Type"] = "stringParmType.Regular"
        return field

    @classmethod
    def from_json(cls, json_object, input_name, field_desc: FieldDesc):
        return cls(json_object['Value Data'][0])

    def get_output(self, json_field, field_desc: FieldDesc, data_field='Value Data', output_index=0):
        json_field[data_field] = [self._value]

    @classmethod
    def get_param_default(cls, json_object, default_value):
        assert isinstance(default_value, str)
        json_object['Default Value'] = [default_value]


# _value is file name
class FileField(Field):
    field_type_name = FILE_TYPE
    support_param = False

    def __init__(self, file_name=None, work_path=None):
        super().__init__(file_name)
        self._work_path = work_path

    @classmethod
    def from_json(cls, json_object, input_name, field_desc: FieldDesc):
        return FileField(json_object['Value Data'], field_desc.work_path)

    def type_assert(self):
        assert isinstance(self._value, str)

    def get_input(self):
        """return absolute path"""
        return os.path.join(self._work_path, self._value).replace("\\", '/')


# _value is file path
class JsonField(Field, ListSubFieldBase):
    field_type_name = JSON_TYPE
    support_param = False

    def __init__(self, value, filename=None, work_path=None):
        super().__init__(value)
        self._filename = filename
        self._work_path = work_path

    @classmethod
    def from_json(cls, json_object, input_name, field_desc: FieldDesc):
        filename = json_object['Value Data'][0]
        file_path = os.path.join(field_desc.work_path, filename).replace("\\", '/')
        f = open(file_path, 'r')
        value = json.loads(f.read())
        return cls(value, filename, field_desc.work_path)

    def get_output(self, json_field, field_desc: FieldDesc, data_field='Value Data', output_index=0):
        if self._filename is None:
            self._filename = "jsonfile_" + json_field['label'] + ".json"
        # save file
        file_path = os.path.join(field_desc.work_path, self._filename).replace('\\', '/')
        f = open(file_path, "w")
        json.dump(self._value, f)
        # fill data field
        json_field[data_field] = [self._filename]

    @classmethod
    def list_to_json_value(cls, val, work_path=None):
        if work_path is None:
            raise Exception("json file as list sub field need work_path")
        file_name = "jsonfile_" + time.strftime("%H%M%S", time.localtime()) + str(next(unique_name_generator)) + ".json"
        file_path = os.path.join(work_path, file_name).replace("\\", '/')
        f = open(file_path, 'w')
        json.dump(val, f)
        return file_name

    @classmethod
    def list_from_json_value(cls, json_value, work_path=None):
        if work_path is None:
            return {}
        file_path = os.path.join(work_path, json_value).replace("\\", "/")
        f = open(file_path, 'r')
        value = json.loads(f.read())
        f.close()
        return value


class ListMeta(FieldMeta):
    """to support sth like 'ListField[Int]' """

    def __getitem__(self, item):
        assert issubclass(item, ListSubFieldBase)
        cls_name = 'ListField' + item.field_type_name
        cls_dict = {cls.__name__: cls for cls in ListField.__subclasses__()}
        if cls_name in cls_dict:
            return cls_dict[cls_name]
        a = ListMeta('ListField' + item.field_type_name, (ListField,), {'inner_field': item})
        a.inner_field = item
        return a


class ListField(Field, metaclass=ListMeta):
    if_list = True
    inner_field = Field
    field_type = LIST_TYPE
    support_param = False

    def __init__(self, values, inner_field_type=None):
        super().__init__(values)
        self.inner_field_type = self.inner_field if inner_field_type is None else inner_field_type

    @classmethod
    def from_json(cls, json_object, input_name, field_desc: FieldDesc):
        values = json_object["Value Data"]
        inner_field_type = FieldManager()[json_object['Data Type']]

        def helper(value):
            return inner_field_type.list_from_json_value(value, field_desc.work_path)

        values = list(map(helper, values))
        return ListField(values, inner_field_type)

    @classmethod
    def create_json_field(cls, field_category=FieldCategory.Input, name: str = None):
        field = {'Type': cls.field_type, 'Data Type': cls.inner_field.field_type_name, 'If List': cls.if_list,
                 'FieldCategory': field_category.name}
        if name is not None:
            field["Label"] = name
        return field

    def get_output(self, json_field, field_desc: FieldDesc, data_field='Value Data', output_index=0):
        def helper(value):
            return self.inner_field_type.list_to_json_value(value, work_path=field_desc.work_path)

        values = list(map(helper, self._value))
        json_field[data_field] = values
