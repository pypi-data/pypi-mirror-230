# -*- coding: utf-8 -*-
"""
Author  : NextPCG
"""

import datetime
import json
import os
import re
import zlib
import numpy as np
from typing import Dict, List
from PIL import Image


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


class Volume(GeoBase):
    def __init__(self):
        super(Volume, self).__init__()
        self.name = ""
        self.volume_info = {}
        self.volume_transform = None
        self.volume_bound_center = None
        self.volume_bound_size = None
        self.mat = None

    def to_json(self, io_mode=1, work_path=None):
        json_data = super().to_json(io_mode, work_path)
        json_data['volume_info'] = self.volume_info
        # TODO: whether correct? x,y 's order
        json_data['xsize'] = np.size(self.mat, 0)
        json_data['ysize'] = np.size(self.mat, 1)
        json_data['volume_name'] = self.name
        if self.volume_bound_size is not None:
            json_data['volume_bound_size'] = self.volume_bound_size
        if self.volume_transform is not None:
            json_data['volume_transform'] = self.volume_transform
        if self.volume_bound_center is not None:
            json_data['volume_bound_center'] = self.volume_bound_center
        return json_data


class HeightField():

    def __init__(self, name=None):
        self.volumes: Dict[str, Volume] = {}

    @staticmethod
    def create_from_json(json_object: Dict, geo_key_list: List[str], work_path: str, io_mode: int, raw_compress: bool):
        heightfield = HeightField()
        geo_idx = -1
        for geo_key in geo_key_list:
            if "Geo_" in geo_key:
                volume = Volume()
                geo_val = json_object[geo_key]
                # geo_name = input_name + "_" + re.split('-|\.', geo_val)[0]
                geo_idx = geo_idx + 1
                geo_path = os.path.join(work_path, geo_val).replace("\\", "/")
                f = open(geo_path, "r", encoding="utf-8")
                geo_json_data = json.loads(f.read())["Output_Geo"]

                hf_size_x = geo_json_data['xsize']
                hf_size_y = geo_json_data['ysize']
                hf_volume_size = 1.0

                if 'volume_transform' in geo_json_data:
                    volume_transform = geo_json_data['volume_transform']

                # add volume
                hf_volume_name = geo_json_data['volume_name']
                hf_volume = np.asarray([]).astype(np.float32)
                volume_filename = os.path.join(work_path, geo_json_data['volume_file'])
                # support raw file
                packed_volume = None
                if volume_filename.endswith('.raw'):
                    dt = None
                    if 'height' in hf_volume_name or 'alphablend' in hf_volume_name:
                        dt = np.uint16
                    else:
                        dt = np.uint8
                    raw = None
                    if raw_compress:
                        with open(volume_filename, 'rb') as f_volume:
                            compress_buffer = f_volume.read()
                            raw = np.frombuffer(zlib.decompress(compress_buffer), dtype=dt)
                    else:
                        raw = np.fromfile(volume_filename, dtype=dt)
                    # reshape to actual size
                    packed_volume = np.transpose(np.reshape(np.asarray(raw), (hf_size_y, hf_size_x, 1)),[1,0,2])
                else:
                    with Image.open(volume_filename) as image:
                        packed_volume = np.transpose(np.reshape(np.asarray(image)), (hf_size_y, hf_size_x, 1), [1,0,2])

                # x y z in packed_volume

                # https://docs.unrealengine.com/4.26/en-US/BuildingWorlds/Landscape/TechnicalGuide/
                # preprocess to get real height
                zscale = 1.0
                if 'height' in hf_volume_name:
                    if 'volume_transform' in geo_json_data:
                        volume_transform = geo_json_data['volume_transform']
                        zscale = volume_transform[5]
                    hf_volume = np.vectorize(lambda x: (float(x) - 32768.0) * (zscale / 128.0))(packed_volume).astype(
                        np.float32)
                elif 'alphablend' in hf_volume_name:
                    hf_volume = np.vectorize(lambda x: (float(int(x) & 0xFFFC)) / 65532.0)(packed_volume).astype(
                        np.float32)
                else:
                    hf_volume = np.vectorize(lambda x: (x / 255.0))(packed_volume).astype(np.float32)
                volume.mat = hf_volume
                # get attribs
                # volume.detail = geo_json_data['attribs']['detail']
                # volume.vertex = geo_json_data['attribs']['vertex']
                # volume.point = geo_json_data['attribs']['point']
                # volume.prim = geo_json_data['attribs']['prim']
                volume.volume_info = geo_json_data['volume_info']
                volume.volume_transform = geo_json_data['volume_transform']
                volume.volume_bound_center = geo_json_data['volume_bound_center']
                volume.volume_bound_size = geo_json_data['volume_bound_size']
                volume.name = hf_volume_name
                add_custom_attributes(volume, geo_json_data, [], io_mode, work_path)

                heightfield.volumes[hf_volume_name] = volume
        return heightfield

    def to_json(self, geo_index: int, output_index, json_field, io_mode=1, work_path=None, raw_compress = False):
        """
        Returns:
            num of volumes
        """
        for volume_name, volume in self.volumes.items():
            json_geo = volume.to_json()
            json_geo_index = 'Geo_{0}'.format(geo_index)
            volume_filename = '{0}_Heightfield{1}_{2}_{3}.raw'.format(json_geo_index, output_index, volume_name,
                                                                      datetime.datetime.now().strftime("%y%m%d_%H%M%S"))
            json_geo['volume_file'] = volume_filename
            json_img_index = 'Img_{0}'.format(geo_index)
            json_field[json_img_index] = volume_filename
            if io_mode == 1:
                json_geo['attribs_filename'] = ''
                json_field[json_geo_index] = save_output_file(work_path,
                                                              '{0}_Heightfield{1}'.format(json_geo_index, output_index),
                                                              json_geo)
            elif io_mode == 2:
                attri_geo_index = 'Attr_{0}'.format(geo_index)
                attribs_filename = '{0}_Heightfield{1}_{2}.attr_raw'.format(json_geo_index, output_index,
                                                                            datetime.datetime.now().strftime(
                                                                                "%y%m%d_%H%M%S"))
                json_geo['attribs_filename'] = attribs_filename
                attribs_filepath = os.path.join(work_path, attribs_filename)
                write_attribs_to_file(attribs_filepath, json_geo)
                json_field[json_geo_index] = save_output_file(work_path,
                                                              '{0}_HeightField{1}'.format(json_geo_index, output_index),
                                                              json_geo)
                json_field[attri_geo_index] = attribs_filename
            else:
                raise Exception("unsupported io mode")

            save_path = os.path.join(work_path, volume_filename)

            packed_volume = np.transpose(volume.mat)
            if 'height' in volume_name:
                volume_zscale = json_geo['volume_info']['transform']['scale'][2]
                packed_volume = np.vectorize(lambda x: np.uint16(x / volume_zscale * 128.0 + 32768.0))(packed_volume)
                image = Image.fromarray(packed_volume.astype(np.uint16), 'I;16')
                image.save(save_path.replace('.raw', '.tiff'))
                if raw_compress:
                    with open(save_path, 'ab+') as f_volume:
                        buffer = packed_volume.tobytes()
                        compress_buffer = zlib.compress(buffer)
                        f_volume.write(compress_buffer)
                else:
                    packed_volume.tofile(save_path)
            elif 'alphablend' in volume_name:
                pass
                # kivlin. UE4.27 not support to set height alpha blend map.
            else:  # weight
                pass
                packed_volume = np.vectorize(lambda x: np.uint8(x * 255.0))(packed_volume)
                # image = Image.fromarray(packed_volume.astype(np.uint8))
                # image.save(save_path)
                if raw_compress:
                    with open(save_path, 'ab+') as f_volume:
                        buffer = packed_volume.tobytes()
                        compress_buffer = zlib.compress(buffer)
                        f_volume.write(compress_buffer)
                else:
                    # image = Image.fromarray(packed_volume.astype(np.uint8))
                    # image.save(save_path)
                    packed_volume.tofile(save_path)
            geo_index += 1
        return len(self.volumes)


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


class TextureNode(GeoBase):

    def __init__(self):
        super(TextureNode, self).__init__()
        self.name: str = ''
        self.volume_info = dict()
        self.bit_depth = 'u8'
        self.channel_count = 0
        self.mat = {
            'r': None,
            'g': None,
            'b': None,
            'a': None,
        }

    def to_json(self, io_mode=1, work_path=None):
        # get each level attributes
        json_data = super().to_json(io_mode, work_path)
        json_data['volume_info'] = self.volume_info
        json_data['volume_name'] = self.name
        json_data['xsize'] = np.size(self.mat['r'], 1)
        json_data['ysize'] = np.size(self.mat['r'], 0)
        json_data['zsize'] = 1
        json_data['bit_depth'] = self.bit_depth
        # channel = 0
        # for mat in self.mat:
        #     if mat:
        #         channel += 1
        json_data['channel_count'] = self.channel_count
        return json_data


class Texture:
    def __init__(self):
        self.texture_nodes: Dict[str, TextureNode] = {}

    @staticmethod
    def create_from_json(json_field: Dict, work_path, io_mode, raw_compress, input_name: str):
        texture = Texture()
        for geo_key, geo_val in json_field.items():
            if 'Geo_' in geo_key:
                geo_name = input_name + '_' + re.split('-|\.', geo_val)[0]
                geo_path = os.path.join(work_path, geo_val)
                geo_json_data = None
                with open(geo_path, 'r', encoding='utf-8') as f:
                    geo_json_data = json.loads(f.read())['Output_Geo']
                # create texture node
                texture.texture_nodes[geo_name] = create_texture_node(geo_json_data, work_path, io_mode, raw_compress)

        return texture

    @staticmethod
    def create_from_images(images):
        texture = Texture()
        i = 1
        for image in images:
            texture.texture_nodes[f'image{i}'] = image2node(image, f'image{i}')
            i += 1
        return texture

    def to_images(self) -> Dict[str, Image.Image]:
        return { name: node2image(texture_node) for name, texture_node in self.texture_nodes.items()}

    def to_json(self, geo_index, output_index, json_field, io_mode=1, work_path=None, raw_compress=False):
        for geo_name, texture_node in self.texture_nodes.items():
            # get base json
            json_geo = texture_node.to_json()

            # get volume filename
            json_geo_index = 'Geo_{0}'.format(geo_index)
            file_name = texture_node.name
            volume_filename = '{0}_volume{1}_{2}_{3}.raw'.format(json_geo_index, output_index, file_name,
                                                                datetime.datetime.now().strftime("%y%m%d_%H%M%S"))
            json_geo['volume_file'] = volume_filename
            json_img_index = 'Img_{0}'.format(geo_index)
            json_field[json_img_index] = volume_filename
            if io_mode == 1:
                json_geo['attribs_filename'] = ''
                json_field[json_geo_index] = save_output_file(work_path,
                                                              '{0}_Volume{1}'.format(json_geo_index, output_index),
                                                              json_geo)
            elif io_mode == 2:
                attr_geo_index = 'Attr_{0}'.format(geo_index)
                attribs_filename = '{0}_Volume{1}_{2}.attr_raw'.format(json_geo_index,
                                                                       output_index,
                                                                       datetime.datetime.now().strftime("%y%m%d_%H%M%S"))
                json_geo['attribs_filename'] = attribs_filename
                attribs_filepath = os.path.join(work_path, attribs_filename)
                write_attribs_to_file(attribs_filepath, json_geo)
                json_field[json_geo_index] = save_output_file(work_path,
                                                              '{0}_Volume{1}'.format(json_geo_index, output_index),
                                                              json_geo)
                json_field[attr_geo_index] = attribs_filename
            else:
                raise Exception("unsupported io mode")

            # bit depth map
            bit_depth_remap = {}
            bit_depth_remap['u8'] = (np.uint8, 255, True)
            bit_depth_remap['u16'] = (np.uint16, 65535, True)
            bit_depth_remap['u32'] = (np.uint16, 4294967295, True)
            bit_depth_remap['f16'] = (np.float16, 1.0, False)
            bit_depth_remap['f32'] = (np.float32, 1.0, False)

            bit_depth = texture_node.bit_depth
            numpy_type, bit_scale, is_integer = bit_depth_remap[bit_depth]

            volume_dict = dict()
            xsize = json_geo['xsize']
            ysize = json_geo['ysize']

            '''
                the transmission in server_houdini is as follow:
                    1. ExportTexture(in UE) -> this step flip the y axis for raw data 
                    2. Houdini Function
                    3. ImportTexture(in UE) -> this step re-flip the y axis for raw data
            '''
            # cause raw data should be flipped to fit transmission based on server_houdini and we choose raw-data to transmit back, so we flipped back here
            for volume_key, volume in texture_node.mat.items():
                if volume is not None:
                    volume_dict[volume_key] = np.flip(np.reshape(np.asarray(volume), (ysize, xsize)), 0)

            # lambda function to decide whether to round
            round_wrapper = None
            if is_integer:
                round_wrapper = lambda x: round(x)
            else:
                round_wrapper = lambda x: x
            combined_volume = None
            channel_count = texture_node.channel_count
            if channel_count == 1:
                r = np.vectorize(lambda x: numpy_type(round_wrapper(x * bit_scale)))(volume_dict['r'])

                combined_volume = r
            elif channel_count == 2:
                r = np.vectorize(lambda x: numpy_type(round_wrapper(x * bit_scale)))(volume_dict['r'])
                g = np.vectorize(lambda x: numpy_type(round_wrapper(x * bit_scale)))(volume_dict['g'])

                combined_volume = np.dstack((r, g))
            elif channel_count == 3:
                r = np.vectorize(lambda x: numpy_type(round_wrapper(x * bit_scale)))(volume_dict['r'])
                g = np.vectorize(lambda x: numpy_type(round_wrapper(x * bit_scale)))(volume_dict['g'])
                b = np.vectorize(lambda x: numpy_type(round_wrapper(x * bit_scale)))(volume_dict['b'])

                combined_volume = np.dstack((r, g, b))
            elif channel_count == 4:
                r = np.vectorize(lambda x: numpy_type(round_wrapper(x * bit_scale)))(volume_dict['r'])
                g = np.vectorize(lambda x: numpy_type(round_wrapper(x * bit_scale)))(volume_dict['g'])
                b = np.vectorize(lambda x: numpy_type(round_wrapper(x * bit_scale)))(volume_dict['b'])
                a = np.vectorize(lambda x: numpy_type(round_wrapper(x * bit_scale)))(volume_dict['a'])

                combined_volume = np.dstack((r, g, b, a))

            save_path = os.path.join(work_path, volume_filename)
            if raw_compress:
                with open(save_path, 'ab+') as f_volume:
                    buffer = combined_volume.tobytes()
                    compress_buffer = zlib.compress(buffer)
                    f_volume.write(compress_buffer)
            else:
                combined_volume.tofile(save_path)

            geo_index += 1


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


def create_texture_node(geo_json_data, work_path, io_mode, raw_compress):
    # volume info
    hf_size_x = geo_json_data['xsize']
    hf_size_y = geo_json_data['ysize']
    hf_volume_name = geo_json_data['volume_name']
    volume_filename = os.path.join(work_path, geo_json_data['volume_file'])

    # bit depth
    bit_depth_remap = dict()
    bit_depth_remap['u8'] = (np.uint8, 255)
    bit_depth_remap['u16'] = (np.uint16, 65535)
    bit_depth_remap['u32'] = (np.uint16, 4294967295)
    bit_depth_remap['f16'] = (np.uint16, 1.0)
    bit_depth_remap['f32'] = (np.uint32, 1.0)

    bit_depth = None
    bit_type = None
    bit_scale = 0
    channel_count = 0

    # check is raw
    is_raw = False
    base_name = os.path.basename(volume_filename)

    if base_name.endswith('.raw'):
        is_raw = True
        bit_depth = geo_json_data['bit_depth']
        channel_count = geo_json_data['channel_count']
        bit_type, bit_scale = bit_depth_remap[bit_depth]

    # support raw file
    raw = None
    if is_raw:
        if raw_compress:
            with open(volume_filename, 'rb') as f_volume:
                compress_buffer = f_volume.read()
                raw = np.asarray(np.frombuffer(zlib.decompress(compress_buffer), dtype=bit_type))
        else:
            raw = np.asarray(np.fromfile(volume_filename, dtype=bit_type))
    else:
        with Image.open(volume_filename) as image:
            channel_count = len(image.getbands())
            hf_size_x, hf_size_y = image.size
            raw = np.asarray(image)
            bit_type = raw.dtype
            if np.issubdtype(bit_type, np.integer):
                bit_scale = np.iinfo(bit_type).max
            else:
                bit_scale = 1.0
            for bit_depth_key in bit_depth_remap.keys():
                if bit_type.type is bit_depth_remap[bit_depth_key][0]:
                    bit_depth = bit_depth_key
                    break

    '''
        the transmission in server_houdini is as follow:
            1. ExportTexture(in UE) -> this step flip the y axis for raw data 
            2. Houdini Function
            3. ImportTexture(in UE) -> this step re-flip the y axis for raw data

    '''
    # cause raw data has been flipped in ExportTexture(in UE),so we flipped back here
    if is_raw:
        raw = np.flip(np.reshape(raw, (hf_size_y, hf_size_x, channel_count)), 0)

    packed_volume = np.reshape(raw, (hf_size_x * hf_size_y, channel_count)).astype(np.float32) / bit_scale
    # split channels
    split_volumes = np.hsplit(packed_volume, channel_count)

    # create texture node
    texture_node = TextureNode()
    texture_node.name = hf_volume_name
    texture_node.volume_info = geo_json_data['volume_info']
    texture_node.bit_depth = bit_depth
    texture_node.channel_count = len(split_volumes)
    for i in range(len(split_volumes)):
        if i == 0:
            texture_node.mat['r'] = np.reshape(split_volumes[i], (hf_size_y, hf_size_x))
        elif i == 1:
            texture_node.mat['g'] = np.reshape(split_volumes[i], (hf_size_y, hf_size_x))
        elif i == 2:
            texture_node.mat['b'] = np.reshape(split_volumes[i], (hf_size_y, hf_size_x))
        elif i == 3:
            texture_node.mat['a'] = np.reshape(split_volumes[i], (hf_size_y, hf_size_x))
    add_custom_attributes(texture_node, geo_json_data, [], io_mode, work_path)

    return texture_node


def image2node(image:Image.Image, name:str):

    # bit depth
    bit_depth_remap = dict()
    bit_depth_remap['u8'] = (np.uint8, 255)
    bit_depth_remap['u16'] = (np.uint16, 65535)
    bit_depth_remap['u32'] = (np.uint16, 4294967295)
    bit_depth_remap['f16'] = (np.uint16, 1.0)
    bit_depth_remap['f32'] = (np.uint32, 1.0)


    channel_count = len(image.getbands())
    size_x, size_y = image.size
    raw = np.asarray(image)
    bit_type = raw.dtype
    if np.issubdtype(bit_type, np.integer):
        bit_scale = np.iinfo(bit_type).max
    else:
        bit_scale = 1.0
    for bit_depth_key in bit_depth_remap.keys():
        if bit_type.type is bit_depth_remap[bit_depth_key][0]:
            bit_depth = bit_depth_key
            break

    packed_volume = np.reshape(raw, (size_x * size_y, channel_count)).astype(np.float32) / bit_scale
    # split channel
    split_volumes = np.hsplit(packed_volume, channel_count)

    # for i in range(len(split_volumes)):
    #     split_volumes[i] = np.flip(split_volumes[i].reshape((size_x, size_y)), 1)

    texture_node = TextureNode()
    texture_node.name = name
    texture_node.bit_depth = bit_depth
    texture_node.channel_count = 4
    # ensure alpha is add
    if len(split_volumes) == 3:
        texture_node.mat['a'] = np.ones((size_y, size_x), dtype=np.float32)
    assert len(split_volumes) >= 3, "assume image has at least 3 channels"
    for i in range(len(split_volumes)):
        if i == 0:
            texture_node.mat['r'] = np.reshape(split_volumes[i], (size_y, size_x))
        elif i == 1:
            texture_node.mat['g'] = np.reshape(split_volumes[i], (size_y, size_x))
        elif i == 2:
            texture_node.mat['b'] = np.reshape(split_volumes[i], (size_y, size_x))
        elif i == 3:
            texture_node.mat['a'] = np.reshape(split_volumes[i], (size_y, size_x))
    return texture_node


def node2image(texture_node: TextureNode) -> Image:
    size_y, size_x = texture_node.mat['r'].shape
    channel_count = texture_node.channel_count
    marks = ['r', 'g', 'b', 'a']
    channels = list(texture_node.mat[marks[i]].reshape(size_x*size_y, 1) for i in range(channel_count))
    raw = np.hstack(channels).reshape(size_y, size_x, channel_count)*255
    raw = raw.astype(np.uint8)
    image = Image.fromarray(raw, mode= "RGB" if channel_count ==3 else "RGBA")
    return image