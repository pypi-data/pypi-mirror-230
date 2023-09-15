import json
import numpy as np
import hou
import os
import re
from PIL import Image
import zlib
import platform

node = hou.pwd()
geo = node.geometry()
# server_text = 0, houdini_text = 1, houdini_binary = 2
io_mode = 1
raw_compress = False
pson_filename = node.parm('pson_filename').eval()
work_path = node.parm('work_path').eval()

attrib_data_type_remap = {}
attrib_data_type_remap[np.float64] = hou.attribData.Float
attrib_data_type_remap[(np.dtype('float64'))] = hou.attribData.Float
attrib_data_type_remap[np.float32] = hou.attribData.Float
attrib_data_type_remap[(np.dtype('float32'))] = hou.attribData.Float
attrib_data_type_remap[np.int64] = hou.attribData.Int
attrib_data_type_remap[(np.dtype('int64'))] = hou.attribData.Int
attrib_data_type_remap[np.int32] = hou.attribData.Int
attrib_data_type_remap[(np.dtype('int32'))] = hou.attribData.Int
attrib_data_type_remap[int] = hou.attribData.Int
attrib_data_type_remap[float] = hou.attribData.Float


def _asarray(a):
    # @highyang: given that np.asarray will infer int32 for int.
    npa = np.asarray(a)
    if npa.dtype == np.int32:
        npa = npa.astype(np.int64)
    return npa

# @highyang: find that np.asarray  will infer int32 for int.
# common
def add_custom_attributes(geo, geo_json_data, skip_list, new_vertices, new_points, new_prims):
    if "attribs" in geo_json_data:
        input_attribs = geo_json_data["attribs"]
        input_vertex_attribs = input_attribs['vertex']
        input_point_attribs = input_attribs['point']
        input_prim_attribs = input_attribs['prim']
        input_detail_attribs = input_attribs['detail']
        input_attribs_list = [input_vertex_attribs, input_point_attribs, input_prim_attribs, input_detail_attribs]
        domain_index = -1
        group_index = -1
        for input_attribs in input_attribs_list:
            domain_index += 1
            for input_attrib_name, input_attrib_val in input_attribs.items():
                if input_attrib_name in skip_list:
                    continue
                if io_mode == 1:
                    input_attrib_data = input_attrib_val["data"] # @highyang
                elif io_mode == 2 or io_mode == 3:
                    attribs_filename = geo_json_data['attribs_filename']
                    attr_info = input_attrib_val
                    input_attrib_data = load_attribs_from_file(attribs_filename, attr_info)
                if domain_index == 0:  # vertex
                    if geo.findVertexAttrib(input_attrib_name) is None:
                        geo.addAttrib(hou.attribType.Vertex, input_attrib_name, input_attrib_data[0])
                    for i in range(0, len(input_attrib_data)):
                        if len(input_attrib_data[i]) == 1:
                            value = input_attrib_data[i][0]
                        else:
                            value = tuple(input_attrib_data[i])
                        if i < len(new_vertices):
                            vertex = new_vertices[i]
                            vertex.setAttribValue(input_attrib_name, value)

                elif domain_index == 1:  # point
                    if geo.findPointAttrib(input_attrib_name) is None:
                        geo.addAttrib(hou.attribType.Point, input_attrib_name, input_attrib_data[0])
                    for i in range(len(input_attrib_data)):
                        if len(input_attrib_data[i]) == 1:
                            value = input_attrib_data[i][0]
                        else:
                            value = tuple(input_attrib_data[i])
                        if i < len(new_points):
                            point = new_points[i]
                            point.setAttribValue(input_attrib_name, value)
                        if input_attrib_name == 'Index' and i == 0:
                            group_index = value
                elif domain_index == 2:  # prim
                    if geo.findPrimAttrib(input_attrib_name) is None:
                        geo.addAttrib(hou.attribType.Prim, input_attrib_name, input_attrib_data[0])
                    for i in range(len(input_attrib_data)):
                        if len(input_attrib_data[i]) == 1:
                            value = input_attrib_data[i][0]
                        else:
                            value = tuple(input_attrib_data[i])
                        if i < len(new_prims):
                            prim = new_prims[i]
                            prim.setAttribValue(input_attrib_name, value)
                elif domain_index == 3: # detail
                    if group_index >= 0:
                        detail_attrib_name = 'group{0}_{1}'.format(group_index, input_attrib_name)
                        if geo.findPrimAttrib(detail_attrib_name) is None:
                            # geo.addAttrib(hou.attribType.Global, detail_attrib_name, tuple(input_attrib_data.flatten(), 0.0))
                            if len(input_attrib_data) > 0 and len(input_attrib_data[0]) > 0:
                                np_type = np.dtype(type(input_attrib_data[0][0]))
                                attrib_data_type = None
                                if np_type in attrib_data_type_remap:
                                    tuple_size = len(input_attrib_data[0])
                                    attrib_data_type = attrib_data_type_remap[np_type]
                                elif np.issubdtype(np_type, np.string_) or np.issubdtype(np_type, np.str_) or np.issubdtype(np_type, np.unicode_):
                                    tuple_size = 1
                                    attrib_data_type = hou.attribData.String
                                geo.addArrayAttrib(hou.attribType.Global, detail_attrib_name, attrib_data_type, tuple_size=tuple_size)
                                geo.setGlobalAttribValue(detail_attrib_name, _asarray(input_attrib_data).flatten().tolist())

        # create group
        if group_index >= 0:
            group_name = 'group{0}'.format(group_index)
            group = geo.findPrimGroup(group_name)
            if group is None:
                group = geo.createPrimGroup(group_name)
            group.add(new_prims)
    return geo


def create_heightfield_node(geo, input_content, is_blast_geo_key_exist, blast_geo_key_list):
    # get editing layer geo_key_list
    geo_key_list_2d = []
    is_contain_editing_layer = False
    for editing_layer_key, editing_layer_val in input_content.items():
        if 'EditingLayer_' in editing_layer_key:
            is_contain_editing_layer = True
            geo_key_list_2d.append(editing_layer_val)
    if not is_contain_editing_layer:
        geo_key_list_2d.append(input_content.keys())

    for geo_key_list in geo_key_list_2d:
        # create input node
        geo_idx = -1
        for geo_key in geo_key_list:
            if hou.updateProgressAndCheckForInterrupt():
                break
            if 'Geo_' in geo_key:
                if is_blast_geo_key_exist and geo_key not in blast_geo_key_list:
                    continue
                geo_val = input_content[geo_key]
                geo_name = input_name + "_" + re.split('-|\.', geo_val)[0]
                geo_idx = geo_idx + 1
                geo_path = os.path.join(work_path, geo_val)  # .replace("\\", "/")
                f = open(geo_path, "r", encoding='utf-8')
                geo_json_data = json.loads(f.read())['Output_Geo']
                # create node
                hf_size_x = geo_json_data['xsize']
                hf_size_y = geo_json_data['ysize']
                # hf_volume_size = geo_json_data['zsize']

                scale_0 = hf_size_y * 0.5
                scale_1 = hf_size_x * 0.5
                scale_2 = 0.05 # zscale not work on volume transform.
                # set center.
                if 'volume_transform' in geo_json_data:
                    volume_transform = geo_json_data['volume_transform']
                    pos_0 = volume_transform[1]
                    pos_1 = volume_transform[0]
                    pos_2 = volume_transform[2]
                    scale_0 *= volume_transform[3]
                    scale_1 *= volume_transform[4]
                elif 'volume_info' in geo_json_data:
                    volume_transform = geo_json_data['volume_info']['transform']
                    pos_0 = volume_transform['position'][2]
                    pos_1 = volume_transform['position'][1]
                    pos_2 = volume_transform['position'][0]
                    scale_0 *= volume_transform['scale'][0]
                    scale_1 *= volume_transform['scale'][1]

                # build transform
                # transform_order = 'srt'
                tr = hou.hmath.identityTransform()
                tr *= hou.hmath.buildScale(scale_0, scale_1, scale_2)
                tr *= hou.hmath.buildRotate(0, 0, 0)
                tr *= hou.hmath.buildTranslate(pos_0, pos_1, pos_2)
                # zx rotation
                tr *= hou.hmath.buildRotate(-90, -90, 0)

                # add volume
                hf_volume_name = geo_json_data['volume_name']
                hf_volume = np.asarray([]).astype(np.float32)
                volume_filename = os.path.join(work_path, geo_json_data['volume_file'])  # .replace("\\", "/")
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
                    packed_volume = np.transpose(np.reshape(np.asarray(raw), (hf_size_y, hf_size_x, 1)))
                    # dont't flip because houdini's landscape coordinate is different.
                    #packed_volume = np.flip(packed_volume)
                else:
                    with Image.open(volume_filename) as image:
                        packed_volume = np.transpose(np.reshape((np.asarray(image)), (hf_size_y, hf_size_x, 1)))
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
                volume = geo.createVolume(hf_size_y, hf_size_x, 1)
                hf_volume = hf_volume.flatten().tolist()
                volume.setAllVoxels(hf_volume)
                volume.setTransform(tr)
                # add name attrib.
                if geo.findPrimAttrib('name') is None:
                    geo.addAttrib(hou.attribType.Prim, 'name', '')
                volume.setAttribValue('name', hf_volume_name)
                # add zscale attrib.
                if geo.findPointAttrib('zscale') is None:
                    geo.addAttrib(hou.attribType.Point, 'zscale', 1.0)
                volume.vertex(0).point().setAttribValue('zscale', zscale)

                # add other attrib.
                add_custom_attributes(geo, geo_json_data, ['name', 'P'], [volume.vertices()[0]], [volume.points()[0]],
                                      [volume])

    return geo


def create_volume_node(geo, geo_json_data, geo_name):
    # create node
    hf_size_x = geo_json_data['xsize']
    hf_size_y = geo_json_data['ysize']
    hf_volume_size = geo_json_data['zsize']
    # add volume
    hf_volume_name = geo_json_data['volume_name']
    volume_filename = os.path.join(work_path, geo_json_data['volume_file'])  # .replace("\\", "/")

    bit_depth_remap = {}
    bit_depth_remap['u8'] = (np.uint8, 255)
    bit_depth_remap['u16'] = (np.uint16, 65535)
    bit_depth_remap['u32'] = (np.uint16, 4294967295)
    bit_depth_remap['f16'] = (np.float16, 1.0)
    bit_depth_remap['f32'] = (np.float32, 1.0)

    bit_type = None
    channel_count = 0
    bit_scale = 0
    # check is raw
    is_raw = False
    base_name = os.path.basename(volume_filename)
    # kivlin. bug occur if volume_filename contain multi dot.
    #if '.' in base_name: # deprecated. use .raw instead.
    #    _, ext = base_name.split('.')
    #    if 'x' in ext:
    #        bit_depth, channel_count = ext.split('x')
    #        channel_count = int(channel_count)
    #    else:
    #        bit_depth = ext
    #        channel_count = 1
    #    if bit_depth in bit_depth_remap.keys():
    #        is_raw = True
    #        bit_type, bit_scale = bit_depth_remap[bit_depth]

    if base_name.endswith('.raw'):
        is_raw = True
        bit_depth = geo_json_data['bit_depth']
        channel_count = geo_json_data['channel_count']
        bit_type, bit_scale = bit_depth_remap[bit_depth]

    # support raw file
    packed_volume = None
    if is_raw:
        raw = None
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
    packed_volume = np.reshape(raw, (hf_size_x * hf_size_y, channel_count)).astype(np.float32) / bit_scale

    split_volumes = np.hsplit(packed_volume, channel_count)
    if not is_raw:
        for i in range(len(split_volumes)):
            split_volumes[i] = np.flip(split_volumes[i].reshape((hf_size_x, hf_size_y)), 0)
    # build transform
    scale_0 = hf_size_x * 0.5
    scale_1 = hf_size_y * 0.5
    # transform_order = 'srt'
    tr = hou.hmath.identityTransform()
    tr *= hou.hmath.buildScale(scale_0, scale_1, 1.0)
    # zx rotation
    tr *= hou.hmath.buildRotate(-90, 0, 0)


    for i in range(len(split_volumes)):
        volume = geo.createVolume(hf_size_x, hf_size_y, 1)
        hf_volume = split_volumes[i].flatten().tolist()
        volume.setAllVoxels(hf_volume)
        volume.setTransform(tr)
        # add name attrib.
        if geo.findPrimAttrib('name') is None:
            geo.addAttrib(hou.attribType.Prim, 'name', '')
        channel = None
        if i == 0:
            channel = 'r'
        if i == 1:
            channel = 'g'
        if i == 2:
            channel = 'b'
        if i == 3:
            channel = 'a'
        volume.setAttribValue('name', '{0}.{1}'.format(hf_volume_name, channel))
        # add bit_depth attrib.
        if geo.findPrimAttrib('bit_depth') is None:
            geo.addAttrib(hou.attribType.Prim, 'bit_depth', '')
        if bit_depth is not None:
            volume.setAttribValue('bit_depth', bit_depth)
        # add other attrib.
        add_custom_attributes(geo, geo_json_data, ['name', 'P'], [volume.vertices()[0]], [volume.points()[0]], [volume])

    return geo


def create_instance_node(geo, geo_json_data, geo_name):
    new_vertices = []
    new_points = []
    new_prims = []

    # create instance.
    pos_buffer = []
    orient_buffer = []
    scale_buffer = []
    if "attribs" in geo_json_data:
        input_val = geo_json_data["attribs"]
        if 'P' in input_val['point'] and 'orient' in input_val['point'] and 'scale' in input_val['point']:
            if io_mode == 1:
                pos_buffer = np.asarray(input_val['point']['P']["data"])
                orient_buffer = np.asarray(input_val['point']['orient']["data"])
                scale_buffer = np.asarray(input_val['point']['scale']["data"])
            elif io_mode == 2 or io_mode == 3:
                pos_buffer = load_attribs_from_file(geo_json_data['attribs_filename'], input_val['point']['P'])
                orient_buffer = load_attribs_from_file(geo_json_data['attribs_filename'], input_val['point']['orient'])
                scale_buffer = load_attribs_from_file(geo_json_data['attribs_filename'], input_val['point']['scale'])
    mesh_geo = None
    if 'instanced_geos' in geo_json_data:
        if '0' in geo_json_data['instanced_geos']:
            if len(geo_json_data['instanced_geos']['0'].keys()) > 0:
                mesh_geo = hou.Geometry()
                mesh_geo = create_mesh_node(mesh_geo, geo_json_data['instanced_geos']['0'], geo_name + '_instanced_geo')
    # one instance point on prim.
    for i in range(len(pos_buffer)):
        pos = pos_buffer[i]
        orient = orient_buffer[i]
        scale = scale_buffer[i]



        point = geo.createPoint()
        point.setPosition(pos)
        new_points.append(point)
        # prim = geo.createPolygon()

        packedprim = geo.createPacked('PackedGeometry', point)

        # build transform
        # transform_order = 'srt'
        tr = hou.hmath.identityTransform()
        tr *= hou.hmath.buildScale(scale[0], scale[1], scale[2])
        tr *= hou.Matrix4(hou.Quaternion(orient[0], orient[1], orient[2], orient[3]).extractRotationMatrix3())
        # tr *= hou.hmath.buildRotate(0, 0, 0)
        tr *= hou.hmath.buildTranslate(pos[0], pos[1], pos[2])
        packedprim.setTransform(tr)

        if mesh_geo is not None:
            packedprim.setEmbeddedGeometry(mesh_geo)

        # prim.setIsClosed(False)
        new_prims.append(packedprim)
        # vertex = packedprim.addVertex(point)
        new_vertices.append(packedprim.vertex(0))

    add_custom_attributes(geo, geo_json_data, ['P'], new_vertices, new_points, new_prims)
    return geo


def create_curve_node(geo, geo_json_data, geo_name):
    new_vertices = []
    new_points = []
    new_prims = []

    # create curve .
    pos_buffer = []
    if "attribs" in geo_json_data:
        input_val = geo_json_data["attribs"]
        for temp in input_val['point']:
            if 'P' in temp:
                if io_mode == 1:
                    pos_buffer = input_val['point'][temp]["data"]
                elif io_mode == 2 or io_mode == 3:
                    attribs_filename = geo_json_data['attribs_filename']
                    attr_info = input_val['point'][temp]
                    pos_buffer = load_attribs_from_file(attribs_filename, attr_info)

    # one curve one prim.
    prim = geo.createPolygon()
    prim.setIsClosed(False)
    new_prims.append(prim)
    for pos in pos_buffer:
        point = geo.createPoint()
        point.setPosition(pos)
        new_points.append(point)
        vertex = prim.addVertex(point)
        new_vertices.append(vertex)

    add_custom_attributes(geo, geo_json_data, ['P'], new_vertices, new_points, new_prims)
    return geo


def create_mesh_node(geo, geo_json_data, geo_name):

    is_create_default_instance_mesh = 'attribs_filename' not in geo_json_data
    new_vertices = []
    new_points = []
    new_prims = []

    # create mesh.
    pos_buffer = []
    face_buffer = []
    if "attribs" in geo_json_data:
        input_val = geo_json_data["attribs"]
        for temp in input_val['point']:
            if 'P' in temp:
                if io_mode == 1 or is_create_default_instance_mesh:
                    pos_buffer = input_val['point'][temp]["data"]
                elif io_mode == 2 or io_mode == 3:
                    attribs_filename = geo_json_data['attribs_filename']
                    attr_info = input_val['point'][temp]
                    pos_buffer = load_attribs_from_file(attribs_filename, attr_info)

    if io_mode == 1 or is_create_default_instance_mesh:
        if "faces" in geo_json_data:
            face_buffer = geo_json_data["faces"] # @highyang
    elif io_mode == 2 or io_mode == 3:
        attribs_filename = geo_json_data['attribs_filename']
        attr_info = input_val['prim']['face_index']
        face_buffer = load_attribs_from_file(attribs_filename, attr_info)
    for pos in pos_buffer:
        point = geo.createPoint()
        point.setPosition(pos)
        new_points.append(point)
    for face in face_buffer:
        prim = geo.createPolygon()
        new_prims.append(prim)
        for index in face:
            vertex = prim.addVertex(new_points[int(index)]) # @highyang: temp type cast
            new_vertices.append(vertex)

    add_custom_attributes(geo, geo_json_data, ['P', 'face_index'], new_vertices, new_points, new_prims)
    return geo

attr_data_type_to_numpy_remap = {}
attr_data_type_to_numpy_remap['i32'] = (np.int32, 1)
attr_data_type_to_numpy_remap['f32'] = (np.float32, 1)
# s in json
attr_data_type_to_numpy_remap['f32x2'] = (np.float32, 2)
attr_data_type_to_numpy_remap['f32x3'] = (np.float32, 3)
attr_data_type_to_numpy_remap['f32x4'] = (np.float32, 4)

def load_attribs_from_file(attribs_filename, attr_info):
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
                if platform.system() == 'Linux':
                    buffer = np.asarray(buffer, dtype=np.int64)
                else: # Windows / Darwin
                    buffer = np.asarray(buffer, dtype=np.int64) # @highyang�� change 32 -> 64
            elif np_type == np.float32:
                buffer = np.asarray(buffer, dtype=np.float64)
    return buffer.tolist()  # @highyang: use list instead np

# step 1. load pson
if len(pson_filename) > 0 and len(work_path) > 0:
    pson = None
    with open(pson_filename, "rb") as f:
        pson = json.load(f)
    # step 1.1. check NEXTPCG_INPUT or NEXTPCG_OUTPUT
    if 'NextPCG_INPUT' in pson:
        pson = pson['NextPCG_INPUT']
    elif 'NextPCG_OUTPUT' in pson:
        pson = pson['NextPCG_OUTPUT']

    # step 2. handling input
    json_data = pson
    input_index = node.parm('input_index').eval()
    input_type = node.parm('input_type').eval()
    debug_output = node.parm('debug_output').eval()
    blast_geo_key = node.parm('blast_geo_key').eval()

    blast_geo_key_list = []
    is_blast_geo_key_exist = len(blast_geo_key)
    if is_blast_geo_key_exist:
        blast_geo_key_list = blast_geo_key.split(' ')

    if 'io_mode' in json_data:
        io_mode = int(json_data['io_mode'])
    if 'raw_compress' in json_data:
        raw_compress = bool(json_data['raw_compress'])

    for json_key, json_value in json_data.items():
        if '.hda' in json_key:
            if 'Inputs' in json_data[json_key]:
                if debug_output:
                    json_input_data = json_data[json_key]['Outputs']
                else:
                    json_input_data = json_data[json_key]['Inputs']
                for input_name, input_content in json_input_data.items():
                    # set_from_input_info
                    if debug_output:
                        current_input_index = int(input_name.replace("output", "")) - 1
                    else:
                        current_input_index = int(input_name.replace("input", "")) - 1
                    current_input_type = input_content['label']
                    if current_input_index == input_index and input_type in current_input_type:
                        if 'Curve' in input_type:
                            for geo_key, geo_val in input_content.items():
                                if hou.updateProgressAndCheckForInterrupt():
                                    break
                                if 'Geo_' in geo_key:
                                    geo_name = input_name + "_" + re.split('-|\.', geo_val)[0]
                                    if is_blast_geo_key_exist and geo_key not in blast_geo_key_list:
                                        continue
                                    geo_path = os.path.join(work_path, geo_val)  # .replace('\\', '/')
                                    f = open(geo_path, 'r', encoding='utf-8')
                                    geo_json_data = json.loads(f.read())['Output_Geo']
                                    f.close()
                                    # create input node
                                    create_curve_node(geo, geo_json_data, geo_name)
                        if 'Mesh' in input_type:
                            for geo_key, geo_val in input_content.items():
                                if hou.updateProgressAndCheckForInterrupt():
                                    break
                                if 'Geo_' in geo_key:
                                    geo_name = input_name + "_" + re.split('-|\.', geo_val)[0]
                                    if is_blast_geo_key_exist and geo_key not in blast_geo_key_list:
                                        continue
                                    geo_path = os.path.join(work_path, geo_val)  # .replace('\\', '/')
                                    f = open(geo_path, 'r', encoding='utf-8')
                                    geo_json_data = json.loads(f.read())['Output_Geo']
                                    f.close()
                                    # create input node
                                    create_mesh_node(geo, geo_json_data, geo_name)
                        if 'Heightfield' in input_type:
                            create_heightfield_node(geo, input_content, is_blast_geo_key_exist, blast_geo_key_list)
                        if 'Instance' in input_type:
                            for geo_key, geo_val in input_content.items():
                                if hou.updateProgressAndCheckForInterrupt():
                                    break
                                if 'Geo_' in geo_key:
                                    geo_name = input_name + "_" + re.split('-|\.', geo_val)[0]
                                    if is_blast_geo_key_exist and geo_key not in blast_geo_key_list:
                                        continue
                                    geo_path = os.path.join(work_path, geo_val)  # .replace('\\', '/')
                                    f = open(geo_path, 'r', encoding='utf-8')
                                    geo_json_data = json.loads(f.read())['Output_Geo']
                                    f.close()
                                    # create input node
                                    create_instance_node(geo, geo_json_data, geo_name)
                        if 'Volume' in input_type:
                            for geo_key, geo_val in input_content.items():
                                if hou.updateProgressAndCheckForInterrupt():
                                    break
                                if 'Geo_' in geo_key:
                                    geo_name = input_name + "_" + re.split('-|\.', geo_val)[0]
                                    if is_blast_geo_key_exist and geo_key not in blast_geo_key_list:
                                        continue
                                    geo_path = os.path.join(work_path, geo_val)  # .replace('\\', '/')
                                    f = open(geo_path, 'r', encoding='utf-8')
                                    geo_json_data = json.loads(f.read())['Output_Geo']
                                    f.close()
                                    # create input node
                                    create_volume_node(geo, geo_json_data, geo_name)
