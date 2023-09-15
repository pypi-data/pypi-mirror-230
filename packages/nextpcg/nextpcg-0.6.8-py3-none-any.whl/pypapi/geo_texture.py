# -*- coding: utf-8 -*-
"""
Author  : NextPCG
"""

import datetime
import json
import os.path
import re
import zlib
import numpy as np

from typing import Dict, List
from PIL import Image
from .geo import GeoBase, add_custom_attributes, save_output_file, write_attribs_to_file


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
