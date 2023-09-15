# -*- coding: utf-8 -*-
"""
Author  : NextPCG
"""

import datetime
import json
import re
from typing import Dict, List
import os
from PIL import Image
from .geo import GeoBase, save_output_file, write_attribs_to_file, load_attribs_from_file, add_custom_attributes

import numpy as np


class InstanceNode(GeoBase):
    """simulate Instance node on houdini"""

    def __init__(self):
        super().__init__()
        self.name: str = ""
        self.positions = []  #
        self.orientations = []  # : quaternion
        self.scales = []
        self.instanced_geos = None

    def to_json(self, io_mode=1, work_path=None):
        json_data = super().to_json(io_mode, work_path)

        # don't support mesh geo now TODO
        # if self.instanced_geos is not None:
        #     json_data['instance_geos'] = self.instanced_geos

        json_mesh_point_data = json_data['attribs']['point']

        if len(self.positions) > 0:
            json_mesh_point_data['P'] = {'type': 1, 'data': self.positions}
        if len(self.orientations) > 0:
            json_mesh_point_data['orient'] = {'type': 1, 'data': self.orientations}
        if len(self.scales) > 0:
            json_mesh_point_data['scale'] = {'type': 1, 'data': self.scales}
        # transform

        if io_mode == 1 or io_mode == 0:
            json_trans = {}
            for point_index in range(len(self.positions)):
                xform = {}
                xform['position'] = json_mesh_point_data['P']['data'][point_index]
                # support default orient and scale for instance.
                orient = [0, 0, 0, 1]
                if 'orient' in json_mesh_point_data:
                    orient = json_mesh_point_data['orient']['data'][point_index]
                scale = [1, 1, 1]
                if 'scale' in json_mesh_point_data:
                    scale = json_mesh_point_data['scale']['data'][point_index]
                xform['rotationQuaternion'] = orient
                xform['scale'] = scale
                xform['sheer'] = [0, 0, 0]
                xform['rstorder'] = 5
                json_trans[str(point_index)] = xform
            json_data['transforms'] = json_trans

        return json_data


def create_instance_node(geo_json_data, geo_name, io_mode, work_path) -> InstanceNode:
    instance_node = InstanceNode()

    new_vertices = []
    new_points = []
    new_prims = []

    # create instance.
    pos_buffer = []
    orient_buffer = []
    scale_buffer = []
    if "attribs" in geo_json_data:
        input_val = geo_json_data['attribs']
        if 'P' in input_val['point'] and 'orient' in input_val['point'] and 'scale' in input_val['point']:
            if io_mode == 0 or io_mode == 1:
                pos_buffer = (input_val['point']['P']['data'])
                orient_buffer = (input_val['point']['orient']['data'])
                scale_buffer = (input_val['point']['scale']['data'])
            elif io_mode == 2 or io_mode == 3:
                pos_buffer = load_attribs_from_file(geo_json_data['attribs_filename'], input_val['point']['P'],
                                                    work_path)
                orient_buffer = load_attribs_from_file(geo_json_data['attribs_filename'], input_val['point']['orient'],
                                                       work_path)
                scale_buffer = load_attribs_from_file(geo_json_data['attribs_filename'], input_val['point']['scale'],
                                                      work_path)

        # not support staticMesh geo yes
        if 'instanced_geos' in geo_json_data:
            instance_node.instanced_geos = geo_json_data['instanced_geos']

    instance_node.positions = pos_buffer
    instance_node.orientations = orient_buffer
    instance_node.scales = scale_buffer

    add_custom_attributes(instance_node, geo_json_data, ['P'], io_mode, work_path)
    return instance_node


class InstancedStaticMesh:
    def __init__(self):
        self.instance_nodes: Dict[str, InstanceNode] = {}

    @staticmethod
    def create_from_json(json_field: Dict, work_path: str, io_mode: int, input_name: str):
        instance_staticmesh = InstancedStaticMesh()
        for geo_key, geo_val in json_field.items():
            if 'Geo_' in geo_key:
                geo_name = input_name + '_' + re.split('-|\.', geo_val)[0]
                geo_path = os.path.join(work_path, geo_val)
                f = open(geo_path, 'r', encoding='utf-8')
                geo_json_data = json.loads(f.read())['Output_Geo']
                f.close()

                # create instance node
                instance_staticmesh.instance_nodes[geo_name] = create_instance_node(geo_json_data, geo_name, io_mode,
                                                                                    work_path)

        return instance_staticmesh

    def to_json(self, geo_index: int, output_index, json_field, io_mode=1, work_path=None):
        for geo_name, instance_node in self.instance_nodes.items():
            json_geo = instance_node.to_json()
            json_geo_index = 'Geo_{0}'.format(geo_index)
            if io_mode == 1 or io_mode == 0:
                json_geo['attribs_filename'] = ''
                json_field[json_geo_index] = save_output_file(work_path,
                                                              '{0}_Instance{1}'.format(json_geo_index, output_index),
                                                              json_geo)
            elif io_mode ==2 or io_mode==3:
                attri_geo_index = "Attr_{0}".format(geo_index)
                attribs_filename = '{0}_Instance{1}_{2}.attr_raw'.format(json_geo_index, output_index, datetime.datetime.now().strftime("%y%m%d_%H%M%S"))
                json_geo['attribs_filename'] = attribs_filename
                abs_attribs_filename = os.path.join(work_path, attribs_filename)
                offset = write_attribs_to_file(abs_attribs_filename, json_geo)

                # mesh geo todo

                json_field[json_geo_index] = save_output_file(work_path,
                                                              '{0}_Instance{1}'.format(json_geo_index, output_index),
                                                              json_geo)
                json_field[attri_geo_index] = attribs_filename
            else:
                raise Exception("unsupported io mode")

            geo_index += 1
        return len(self.instance_nodes)
