# -*- coding: utf-8 -*-
"""
Author  : NextPCG
"""

import datetime
import json
import os
import zlib

import numpy as np


class GeoBase:
    """base for mesh, heightfield"""

    def __init__(self):
        self.detail = {}
        self.vertex = {}
        self.point = {}
        self.prim = {}

    def to_json(self, io_mode=1, work_path=None):
        json_data = {}

        json_data['part_info'] = {}
        json_data['point_count'] = 1
        json_data['vertex_count'] = 1
        json_data['face_count'] = 1
        json_data['detail_count'] = 0

        json_mesh_data = {}
        json_mesh_data['point'] = self.point
        json_mesh_data['prim'] = self.prim
        json_mesh_data['vertex'] = self.vertex
        json_mesh_data['detail'] = self.detail

        json_data['attribs'] = json_mesh_data

        return json_data

    def add_attribute(self, domain_index, attrib_name, attrib_data):
        """
        add custom attribute
        :param domain_index: 0->vertex, 1->point, 2->prim, 3->detail
        :param attrib_name: name of the attribute you want to add
        :param attrib_data: data of the attribute you want to add
        :return: True if success
        """
        if domain_index < 0 or domain_index > 3:
            return False
        domain = None
        if domain_index == 0:
            domain = self.vertex
        elif domain_index == 1:
            domain = self.point
        elif domain_index == 2:
            domain = self.prim
        elif domain_index == 3:
            domain = self.detail
        domain[attrib_name] = {}
        domain[attrib_name]['type'] = domain_index
        domain[attrib_name]['data'] = attrib_data
        return True


"""helper functions"""


def save_output_file(output_path, json_geo_index, json_geo):
    geo_filename = json_geo_index + '_' + datetime.datetime.now().strftime("%y%m%d_%H%M%S") + '.json'
    save_path = os.path.join(output_path, geo_filename)  # .replace("\\", "/")
    save_data = {'Output_Geo': json_geo}
    with open(save_path, "w") as f:
        json.dump(save_data, f)
    return geo_filename


numpy_to_attr_data_type_remap = {}
numpy_to_attr_data_type_remap[(np.int32, 1)] = 'i32'
numpy_to_attr_data_type_remap[(np.dtype('int32'), 1)] = 'i32'
numpy_to_attr_data_type_remap[(np.float32, 1)] = 'f32'
numpy_to_attr_data_type_remap[(np.dtype('float32'), 1)] = 'f32'
# s in json
numpy_to_attr_data_type_remap[(np.float32, 2)] = 'f32x2'
numpy_to_attr_data_type_remap[(np.dtype('float32'), 2)] = 'f32x2'
numpy_to_attr_data_type_remap[(np.float32, 3)] = 'f32x3'
numpy_to_attr_data_type_remap[(np.dtype('float32'), 3)] = 'f32x3'
numpy_to_attr_data_type_remap[(np.float32, 4)] = 'f32x4'
numpy_to_attr_data_type_remap[(np.dtype('float32'), 4)] = 'f32x4'


def write_attribs_to_file(attribs_filepath, json_geo, current_offset=0):
    attribs = json_geo['attribs']
    attribs_domain_list = [attribs['vertex'], attribs['point'], attribs['prim'], attribs['detail']]
    with open(attribs_filepath, 'ab+') as f:
        for attribs_domain in attribs_domain_list:
            for attrib_name in attribs_domain:
                attr_info = attribs_domain[attrib_name]
                f.seek(current_offset)
                attr_info['offset'] = current_offset
                data = np.asarray(attr_info['data'])
                del attr_info['data']
                if data.dtype == np.float64:
                    data = data.astype(np.float32)
                if data.dtype == np.int64:
                    data = data.astype(np.int32)
                np_type = data.dtype
                shape = data.shape
                channel_count = 1
                if len(shape) == 2:
                    channel_count = int(shape[1])
                if (np_type, channel_count) in numpy_to_attr_data_type_remap:
                    data_type = numpy_to_attr_data_type_remap[(np_type, channel_count)]
                    buffer = np.asarray(data).tobytes()
                elif np.issubdtype(np_type, np.string_) or np.issubdtype(np_type, np.str_) or np.issubdtype(np_type,
                                                                                                            np.unicode_):
                    data_type = 's'
                    buffer = json.dumps(data.tolist()).encode('utf-8')  # @highyang
                else:
                    raise Exception(
                        'write_attribs_to_file error: name: {0}, type: {1}, channel_count: {2}'.format(attrib_name,
                                                                                                       np_type,
                                                                                                       channel_count))
                compress_buffer = zlib.compress(buffer)
                f.write(compress_buffer)
                attr_info['data_type'] = data_type
                attr_info['length'] = len(compress_buffer)
                attr_info['raw_length'] = len(buffer)
                current_offset += attr_info['length']
    return current_offset


attr_data_type_to_numpy_remap = {}
attr_data_type_to_numpy_remap['i32'] = (np.int32, 1)
attr_data_type_to_numpy_remap['f32'] = (np.float32, 1)
# s in json
attr_data_type_to_numpy_remap['f32x2'] = (np.float32, 2)
attr_data_type_to_numpy_remap['f32x3'] = (np.float32, 3)
attr_data_type_to_numpy_remap['f32x4'] = (np.float32, 4)


def load_attribs_from_file(attribs_filename, attr_info, work_path):
    """in binary mode, load attribs"""
    offset = attr_info['offset']
    length = attr_info['length']
    raw_length = attr_info['raw_length']
    data_type = attr_info['data_type']
    with open(os.path.join(work_path, attribs_filename), 'rb') as f:
        f.seek(offset)
        compress_buffer = f.read(length)
        raw = zlib.decompress(compress_buffer)
        if 's' in data_type:
            buffer = np.asarray(json.loads(raw))
        else:
            (np_type, channel_count) = attr_data_type_to_numpy_remap[data_type]
            buffer = np.asarray(np.frombuffer(raw, dtype=np_type))
            buffer = np.reshape(buffer, (int(len(buffer) / int(channel_count)), int(channel_count)))
            if np_type == np.int32:
                buffer = np.asarray(buffer, dtype=np.int64)  # @highyang�� change 32 -> 64
            elif np_type == np.float32:
                buffer = np.asarray(buffer, dtype=np.float64)
    return buffer.tolist()  # @highyang: use list instead np


def add_custom_attributes(geo: GeoBase, geo_json_data, skip_list, io_mode=1, work_path=""):
    if "attribs" in geo_json_data:
        input_attribs = geo_json_data["attribs"]
        input_vertex_attribs = input_attribs['vertex']
        input_point_attribs = input_attribs['point']
        input_prim_attribs = input_attribs['prim']
        input_detail_attribs = input_attribs['detail']
        input_attribs_list = [input_vertex_attribs, input_point_attribs, input_prim_attribs, input_detail_attribs]
        domain_index = -1  # used to indicate vertex, point, prim, detail
        group_index = -1

        def add_attib_data(domain_json, domain_index, input_attrib_name, input_data):
            domain_json[input_attrib_name] = {}
            domain_json[input_attrib_name]['type'] = domain_index
            domain_json[input_attrib_name]['data'] = input_data

        for input_attribs in input_attribs_list:
            domain_index += 1
            for input_attrib_name, input_attrib_val in input_attribs.items():
                if input_attrib_name in skip_list:
                    continue
                input_attrib_data = []
                if io_mode == 1:
                    input_attrib_data = input_attrib_val["data"]  # @highyang
                elif io_mode == 2 or io_mode == 3:
                    attribs_filename = geo_json_data['attribs_filename']
                    attr_info = input_attrib_val
                    input_attrib_data = load_attribs_from_file(attribs_filename, attr_info, work_path)
                if domain_index == 0:  # vertex
                    add_attib_data(geo.vertex, domain_index, input_attrib_name, input_attrib_data)
                elif domain_index == 1:  # point
                    add_attib_data(geo.point, domain_index, input_attrib_name, input_attrib_data)
                elif domain_index == 2:  # prim
                    add_attib_data(geo.prim, domain_index, input_attrib_name, input_attrib_data)
                elif domain_index == 3:  # detail
                    add_attib_data(geo.detail, domain_index, input_attrib_name, input_attrib_data)
        #     # create group
        # if group_index >= 0:
        #     group_name = 'group{0}'.format(group_index)
        #     group = geo.findPrimGroup(group_name)
        #     if group is None:
        #         group = geo.createPrimGroup(group_name)
        #     group.add(new_prims)
    return geo
