# -*- coding: utf-8 -*-
"""
Author  : NextPCG
"""

import datetime
import json
import zlib
from typing import Dict, List
import os
from PIL import Image
from .geo import GeoBase, save_output_file, write_attribs_to_file, add_custom_attributes

import numpy as np


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