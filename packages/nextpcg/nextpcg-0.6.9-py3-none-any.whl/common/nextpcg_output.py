import json
import os
import hou
import datetime
import numpy as np
import io
from PIL import Image
import zlib

node = hou.pwd()
geo = node.geometry()

# server_text = 0, houdini_text = 1, houdini_binary = 2
io_mode = 1
raw_compress = False
pson_filename = node.parm('pson_filename').eval()
work_path = node.parm('work_path').eval()

# common
def base_save_to_json(prims, override_points, json_data, output_type_name, local_geo, local_group_name):
    vertices = []
    points = []
    face_indices_list = []
    points_index_remap = {}
    for prim in prims:
        face_indices = []
        for vertex in prim.vertices():
            point = vertex.point()
            global_point_number = point.number()
            if global_point_number not in points_index_remap:
                points_index_remap[global_point_number] = len(points)
                points.append(point)
            point_index = points_index_remap[global_point_number]
            face_indices.append(float(point_index))
            vertices.append(vertex)
        face_indices_list.append(face_indices)

    # override points for instance without prims.
    if len(prims) == 0 and override_points != 0:
        points = override_points

    # group_name = input_prim_group.name()
    # geo = input_prim_group.geometry()
    # points = geo.globPoints(group_name)
    # vertices = geo.globVertices(group_name)
    # prims = geo.globPrims(group_name)

    json_data['part_info'] = {}
    json_data['point_count'] = len(points)
    json_data['vertex_count'] = len(vertices)
    json_data['face_count'] = len(prims)
    json_data['detail_count'] = 0

    # attributes
    # kivlin, fix different type with same name.
    json_mesh_data = {}
    json_mesh_vertex_data = {}
    json_mesh_point_data = {}
    json_mesh_prim_data = {}
    json_mesh_detail_data = {}

    io_mode_binary = io_mode == 2 or io_mode == 3
    if io_mode_binary and 'Mesh' in output_type_name:
        json_mesh_prim_data['face_index'] = {}
        json_mesh_prim_data['face_index']['type'] = 2
        json_mesh_prim_data['face_index']['data'] = face_indices_list

    vertex_attribs = local_geo.vertexAttribs()
    point_attribs = local_geo.pointAttribs()
    prim_attribs = local_geo.primAttribs()
    detail_attribs = local_geo.globalAttribs()

    for vertex_attrib in vertex_attribs:
        attrib_list = []
        attrib_name = vertex_attrib.name()
        for vertex in vertices:
            attrib_value = vertex.attribValue(attrib_name)
            if type(attrib_value) is tuple:
                attrib_value = list(attrib_value)
            else:
                attrib_value = [attrib_value]
            attrib_list.append(attrib_value)
        json_mesh_vertex_data[attrib_name] = {}
        json_mesh_vertex_data[attrib_name]['type'] = 0
        json_mesh_vertex_data[attrib_name]['data'] = attrib_list
    for point_attrib in point_attribs:
        attrib_list = []
        attrib_name = point_attrib.name()
        for point in points:

            attrib_value = point.attribValue(attrib_name)
            if type(attrib_value) is tuple:
                attrib_value = list(attrib_value)
            else:
                attrib_value = [attrib_value]
            attrib_list.append(attrib_value)
        json_mesh_point_data[attrib_name] = {}
        json_mesh_point_data[attrib_name]['type'] = 1
        json_mesh_point_data[attrib_name]['data'] = attrib_list
    for prim_attrib in prim_attribs:
        attrib_list = []
        attrib_name = prim_attrib.name()
        for prim in prims:
            attrib_value = prim.attribValue(attrib_name)
            if type(attrib_value) is tuple:
                attrib_value = list(attrib_value)
            else:
                attrib_value = [attrib_value]
            attrib_list.append(attrib_value)
        json_mesh_prim_data[attrib_name] = {}
        json_mesh_prim_data[attrib_name]['type'] = 2
        json_mesh_prim_data[attrib_name]['data'] = attrib_list

    for detail_attrib in detail_attribs:
        attrib_list = []
        attrib_name = detail_attrib.name()
        if attrib_name.startswith('{0}_'.format(local_group_name)):
            data_type = detail_attrib.dataType()
            tuple_size = detail_attrib.size()
            if data_type == hou.attribData.Int:
                attrib_list = geo.intListAttribValue(attrib_name)
            elif data_type == hou.attribData.Float:
                attrib_list = geo.floatListAttribValue(attrib_name)
            elif data_type == hou.attribData.String:
                attrib_list = geo.stringListAttribValue(attrib_name)

            # highyang: add int cast
            attrib_list = np.reshape(np.asarray(attrib_list), (int(len(attrib_list) / tuple_size), tuple_size)).tolist()

            attrib_name = attrib_name.replace('{0}_'.format(local_group_name), '')
        else:
            continue
        json_mesh_detail_data[attrib_name] = {}
        json_mesh_detail_data[attrib_name]['type'] = 3
        json_mesh_detail_data[attrib_name]['data'] = attrib_list

    json_mesh_data['vertex'] = json_mesh_vertex_data
    json_mesh_data['point'] = json_mesh_point_data
    json_mesh_data['prim'] = json_mesh_prim_data
    json_mesh_data['detail'] = json_mesh_detail_data
    json_data['attribs'] = json_mesh_data

    # mesh data
    if 'Mesh' in output_type_name:
        if io_mode == 1:
            json_data["faces"] = face_indices_list

    # curve data
    if 'Curve' in output_type_name:
        pass

    # instance data
    if 'Instance' in output_type_name:
        json_data['instanced_geos'] = {}
        if io_mode == 1:
            json_trans = {}
            for point_index in range(len(points)):
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

    # heightfield data
    if 'Heightfield' in output_type_name:
        volume = prims[0]
        resolution = volume.resolution()
        transform = volume.transform()
        bound = volume.boundingBox()
        json_data['volume'] = volume.allVoxels()
        json_data['volume_name'] = json_mesh_prim_data['name']['data'][0][0]
        xsize = resolution[0]
        ysize = resolution[1]
        json_data['xsize'] = xsize
        json_data['ysize'] = ysize
        json_data['zsize'] = resolution[2]
        json_data['volume_info'] = {}
        json_data['volume_info']['transform'] = {}

        bound_center = bound.center()
        bound_size = bound.sizevec()
        json_data['volume_bound_center'] = [bound_center.x(), bound_center.y(), bound_center.z()]
        json_data['volume_bound_size'] = [bound_size.x() * ((xsize - 1.0) / (xsize)), bound_size.y(), bound_size.z() * ((ysize - 1.0) / (ysize))]

        # rotate back the transform, and we can get the scale
        transform4x4 = hou.Matrix4(transform)
        scale = transform4x4.extractScales()

        # @hihgyang: in case zscale is not in attrib
        zscale = 1.0
        if volume.geometry().findPointAttrib('zscale') is not None:
            zscale = volume.vertex(0).point().attribValue('zscale')
        
        json_data['volume_info']['transform']['scale'] = (scale[0], scale[1], zscale)
        position = volume.vertex(0).point().position()
        json_data['volume_info']['transform']['position'] = (position[0], position[1], position[2])
        json_data['volume_info']['transform']['rotationQuaternion'] = (0, 0, 0, 1)

    # volume data
    if 'Volume' in output_type_name:
        volume = prims[0]
        resolution = volume.resolution()
        transform = volume.transform()
        json_data['volume'] = volume.allVoxels()
        json_data['volume_name'] = json_mesh_prim_data['name']['data'][0][0]
        json_data['xsize'] = resolution[0]
        json_data['ysize'] = resolution[1]
        json_data['zsize'] = resolution[2]


# kivlin, use next_output to add custom output_index:
def is_output_index_match(output_index, item_value):
    if 'index' not in item_value:
        return True
    else:
        dst_output_index = item_value['index']
        src_output_index = output_index
        is_match = src_output_index == dst_output_index
        return is_match

    return True


def save_output_file(output_path, json_geo_index, json_geo):
    geo_filename = json_geo_index + '_' + datetime.datetime.now().strftime("%y%m%d_%H%M%S") + '.json'
    save_path = os.path.join(output_path, geo_filename)  # .replace("\\", "/")
    save_data = {'Output_Geo': json_geo}
    with open(save_path, "w") as f:
        json.dump(save_data, f)
    return geo_filename


def remove_redundant_keys(json_output_inner_data):
    keys = json_output_inner_data.keys()
    redundant_keys = []
    for key in keys:
        key = str(key)
        if key.startswith('Geo') or key.startswith('Img_') or key.startswith('EditingLayer_') or key.startswith('Attr_'):
            redundant_keys.append(key)

    for redundant_key in redundant_keys:
        del json_output_inner_data[redundant_key]

def get_to_output_info(input_prim_groups, input_point_groups, output_path, json_output_data):

    if geo.findPointAttrib('output_index') is None:
        return

    remove_redudant_sets = {}
    remove_redudant_sets['Curve'] = []
    remove_redudant_sets['Mesh'] = []
    remove_redudant_sets['Instance'] = []
    remove_redudant_sets['Heightfield'] = []
    remove_redudant_sets['Volume'] = []

    geo_index = -1
    for input_prim_group in input_prim_groups:
        if hou.updateProgressAndCheckForInterrupt():
            break
        group_name = ''
        if hasattr(input_prim_group, 'name'):
            group_name = input_prim_group.name()
        prims = input_prim_group.prims()
        output_index = -1
        if len(prims) > 0 and len(prims[0].points()) > 0:
            output_index = prims[0].points()[0].attribValue('output_index')
        else:
            pass
            # if hasattr(input_prim_group, 'points'): # geo
            #    if len(input_prim_group.points()) > 0:
            #        output_index = input_prim_group.points()[0].attribValue('output_index')
                # override_points = input_prim_group.points()

        if output_index < 0:
            continue
        for item_key, item_value in json_output_data.items():
            if hou.updateProgressAndCheckForInterrupt():
                break
            # kivlin, use next_output to add custom output_index:
            if is_output_index_match(output_index, item_value) is False:
                continue
            if 'Curve' in item_value['label']:
                if output_index not in remove_redudant_sets['Curve']:
                    remove_redudant_sets['Curve'].append(output_index)
                    remove_redundant_keys(json_output_data[item_key])
                json_geo = {}
                base_save_to_json(prims, [], json_geo, 'Curve', geo, group_name)
                geo_index += 1
                json_geo_index = 'Geo_{0}'.format(geo_index)
                if io_mode == 1:
                    json_geo['attribs_filename'] = ''
                    json_output_data[item_key][json_geo_index] = save_output_file(output_path, '{0}_Curve{1}'.format(json_geo_index, output_index), json_geo)
                elif io_mode == 2 or io_mode == 3:
                    attr_geo_index = 'Attr_{0}'.format(geo_index)
                    attribs_filename = '{0}_Curve{1}_{2}.attr_raw'.format(json_geo_index, output_index, datetime.datetime.now().strftime("%y%m%d_%H%M%S"))
                    json_geo['attribs_filename'] = attribs_filename
                    abs_attribs_filename = os.path.join(work_path, attribs_filename)
                    write_attribs_to_file(abs_attribs_filename, json_geo)
                    json_output_data[item_key][json_geo_index] = save_output_file(output_path, '{0}_Curve{1}'.format(json_geo_index, output_index), json_geo)
                    json_output_data[item_key][attr_geo_index] = attribs_filename

            elif 'Mesh' in item_value['label']:
                if output_index not in remove_redudant_sets['Mesh']:
                    remove_redudant_sets['Mesh'].append(output_index)
                    remove_redundant_keys(json_output_data[item_key])
                json_geo = {}
                base_save_to_json(prims, [], json_geo, 'Mesh', geo, group_name)
                geo_index += 1
                json_geo_index = 'Geo_{0}'.format(geo_index)
                if io_mode == 1:
                    json_geo['attribs_filename'] = ''
                    json_output_data[item_key][json_geo_index] = save_output_file(output_path, '{0}_Mesh{1}'.format(json_geo_index, output_index), json_geo)
                elif io_mode == 2 or io_mode == 3:
                    attr_geo_index = 'Attr_{0}'.format(geo_index)
                    attribs_filename = '{0}_Mesh{1}_{2}.attr_raw'.format(json_geo_index, output_index, datetime.datetime.now().strftime("%y%m%d_%H%M%S"))
                    json_geo['attribs_filename'] = attribs_filename
                    abs_attribs_filename = os.path.join(work_path, attribs_filename)
                    write_attribs_to_file(abs_attribs_filename, json_geo)
                    json_output_data[item_key][json_geo_index] = save_output_file(output_path, '{0}_Mesh{1}'.format(json_geo_index, output_index), json_geo)
                    json_output_data[item_key][attr_geo_index] = attribs_filename

            elif 'Instance' in item_value['label']:
                if output_index not in remove_redudant_sets['Instance']:
                    remove_redudant_sets['Instance'].append(output_index)
                    remove_redundant_keys(json_output_data[item_key])
                json_geo = {}
                base_save_to_json(prims, [], json_geo, 'Instance', geo, group_name)
                # mesh geo
                mesh_geo = None
                if len(prims) > 0:
                    try:
                        mesh_geo = prims[0].getEmbeddedGeometry()
                    except Exception as e:
                        pass
                if mesh_geo is not None:
                    mesh_group_name = ''
                    mesh_prim_group = mesh_geo.primGroups()
                    if len(mesh_prim_group):
                        mesh_group_name = mesh_prim_group[0].name()
                    mesh_json_geo = {}
                    base_save_to_json(mesh_geo.prims(), [], mesh_json_geo, 'Mesh', mesh_geo, mesh_group_name)
                    json_geo['instanced_geos'] = {}
                    json_geo['instanced_geos']['0'] = mesh_json_geo

                geo_index += 1
                json_geo_index = 'Geo_{0}'.format(geo_index)
                if io_mode == 1:
                    json_geo['attribs_filename'] = ''
                    json_output_data[item_key][json_geo_index] = save_output_file(output_path, '{0}_Instance{1}'.format(json_geo_index, output_index), json_geo)
                elif io_mode == 2 or io_mode == 3:
                    attr_geo_index = 'Attr_{0}'.format(geo_index)
                    attribs_filename = '{0}_Instance{1}_{2}.attr_raw'.format(json_geo_index, output_index, datetime.datetime.now().strftime("%y%m%d_%H%M%S"))
                    json_geo['attribs_filename'] = attribs_filename
                    abs_attribs_filename = os.path.join(work_path, attribs_filename)
                    offset = write_attribs_to_file(abs_attribs_filename, json_geo)
                    # mesh geo
                    if mesh_geo is not None:
                        mesh_json_geo['attribs_filename'] = attribs_filename
                        write_attribs_to_file(abs_attribs_filename, mesh_json_geo, offset)
                        json_geo['instanced_geos']['0'] = mesh_json_geo
                    json_output_data[item_key][json_geo_index] = save_output_file(output_path, '{0}_Instance{1}'.format(json_geo_index, output_index), json_geo)
                    json_output_data[item_key][attr_geo_index] = attribs_filename

            elif 'Heightfield' in item_value['label']:
                if output_index not in remove_redudant_sets['Heightfield']:
                    remove_redudant_sets['Heightfield'].append(output_index)
                    remove_redundant_keys(json_output_data[item_key])
                for prim in prims:
                    json_geo = {}
                    base_save_to_json([prim], [], json_geo, 'Heightfield', geo, group_name)
                    geo_index += 1
                    json_geo_index = 'Geo_{0}'.format(geo_index)

                    xsize = json_geo['xsize']
                    ysize = json_geo['ysize']

                    # xy -> yx
                    json_geo['xsize'] = ysize
                    json_geo['ysize'] = xsize

                    zsize = json_geo['zsize']
                    volume = json_geo['volume']
                    volume_name = json_geo['volume_name']
                    if 'volume_editing_layer_index' in json_geo['attribs']['point']:
                        json_geo['volume_editing_layer_index'] = \
                        json_geo['attribs']['point']['volume_editing_layer_index']['data'][0][0]

                    # packed_volume = np.transpose(np.reshape(np.asarray(volume), (xsize, ysize)))
                    packed_volume = np.transpose(np.reshape(np.asarray(volume), (ysize, xsize)))
                    # kivlin. dont flip houdini landscape because coordinate is different.
                    # packed_volume = np.flip(packed_volume)

                    # calculate volume_zscale and volume_center.
                    if 'height' in volume_name:
                        # divide the volume origin zscale
                        transform = json_geo['volume_info']['transform']
                        volume_zscale = transform['scale'][2]

                        # kivlin. we would not send transform back. so we need to use the input volume_zscale
                        # volume_zscale = 1.0
                        # volume_min = np.min(packed_volume)
                        # volume_max = np.max(packed_volume)
                        # volume_zscale = max(max(abs(volume_max), abs(volume_min)) / 256.0, 1.0)

                        # kivlin
                        # t: y,z,x -> x,y,z in ue
                        # r: ?
                        # s: houdini scale == half szie of volume. ue scale is transform.

                        json_geo['volume_transform'] = [(transform['position'][0]), (transform['position'][2]),
                                                        (transform['position'][1]),
                                                        transform['scale'][0] * 2.0 / xsize, transform['scale'][1] * 2.0 / ysize,
                                                        volume_zscale,
                                                        transform['rotationQuaternion'][0],
                                                        transform['rotationQuaternion'][1],
                                                        transform['rotationQuaternion'][2],
                                                        transform['rotationQuaternion'][3]]

                    json_geo['volume'] = []
                    volume_filename = '{0}_Heightfield{1}_{2}_{3}.raw'.format(json_geo_index, output_index, volume_name, datetime.datetime.now().strftime("%y%m%d_%H%M%S"))
                    json_geo['volume_file'] = volume_filename
                    json_img_index = 'Img_{0}'.format(geo_index)
                    json_output_data[item_key][json_img_index] = json_geo['volume_file']
                    if io_mode == 1:
                        json_geo['attribs_filename'] = ''
                        json_output_data[item_key][json_geo_index] = save_output_file(output_path,'{0}_Heightfield{1}'.format(json_geo_index, output_index),json_geo)
                    elif io_mode == 2 or io_mode == 3:
                        attr_geo_index = 'Attr_{0}'.format(geo_index)
                        attribs_filename = '{0}_Heightfield{1}_{2}.attr_raw'.format(json_geo_index, output_index, datetime.datetime.now().strftime("%y%m%d_%H%M%S"))
                        json_geo['attribs_filename'] = attribs_filename
                        abs_attribs_filename = os.path.join(work_path, attribs_filename)
                        write_attribs_to_file(abs_attribs_filename, json_geo)
                        json_output_data[item_key][json_geo_index] = save_output_file(output_path,'{0}_Heightfield{1}'.format(json_geo_index, output_index),json_geo)
                        json_output_data[item_key][attr_geo_index] = attribs_filename

                    save_path = os.path.join(output_path, volume_filename)  # .replace("\\", "/")

                    if 'height' in volume_name:
                        # pass
                        packed_volume = np.vectorize(lambda x: np.uint16((x / volume_zscale * 128.0 + 32768.0)))(
                            packed_volume)
                        #  kivin. we can preview raw in nextpcg admin. so we dont need tiff.
                        #image = Image.fromarray(packed_volume.astype(np.uint16), 'I;16')
                        #image.save(save_path.replace('.raw', '.tiff'))
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
                        # packed_volume = np.vectorize(lambda x : np.uint16(x * 65532.0))(packed_volume)
                        # image = Image.fromarray(packed_volume.astype(np.uint16))
                        # image.save(save_path)
                    else:  # weight
                        packed_volume = np.vectorize(lambda x: np.uint8(x * 255.0))(packed_volume)
                        if raw_compress:
                            with open(save_path, 'ab+') as f_volume:
                                buffer = packed_volume.tobytes()
                                compress_buffer = zlib.compress(buffer)
                                f_volume.write(compress_buffer)
                        else:
                            # image = Image.fromarray(packed_volume.astype(np.uint8))
                            # image.save(save_path)
                            packed_volume.tofile(save_path)

            elif 'Volume' in item_value['label']:
                if output_index not in remove_redudant_sets['Volume']:
                    remove_redudant_sets['Volume'].append(output_index)
                    remove_redundant_keys(json_output_data[item_key])
                geo_index += 1
                json_geo_index = 'Geo_{0}'.format(geo_index)
                delay_volume_dict = {}
                # get channel count:
                channel_count = min(len(prims), 4)

                bit_depth_remap = {}
                bit_depth_remap['u8'] = (np.uint8, 255, True)
                bit_depth_remap['u16'] = (np.uint16, 65535, True)
                bit_depth_remap['u32'] = (np.uint16, 4294967295, True)
                bit_depth_remap['f16'] = (np.float16, 1.0, False)
                bit_depth_remap['f32'] = (np.float32, 1.0, False)

                for prim in prims:
                    json_geo = {}
                    base_save_to_json([prim], [], json_geo, 'Volume', geo, group_name)
                    volume_name = json_geo['volume_name']
                    xsize = json_geo['xsize']
                    ysize = json_geo['ysize']
                    zsize = json_geo['zsize']
                    volume = json_geo['volume']
                    json_geo['volume'] = []

                    if '.' in volume_name:
                        file_name, channel = volume_name.split('.')
                    else:
                        continue

                    # bit_depth for texture
                    # u8, 16, u32, f16, f32
                    if 'r' in channel:
                        bit_depth = 'u8'
                        if geo.findPrimAttrib('bit_depth') is not None:
                            bit_depth = prim.attribValue('bit_depth')

                        volume_filename = '{0}_volume{1}_{2}_{3}.raw'.format(json_geo_index, output_index, file_name,
                                                                datetime.datetime.now().strftime("%y%m%d_%H%M%S"))
                        # volume_filename = json_geo_index + file_name + '.{0}x{1}'.format(bit_depth, channel_count)
                        json_geo['volume_name'] = file_name  # remove .r
                        save_path = os.path.join(output_path, volume_filename)  # .replace("\\", "/")
                        delay_volume_dict['file'] = save_path
                        delay_volume_dict['bit_depth'] = bit_depth

                        json_geo['volume'] = []
                        json_geo['volume_file'] = volume_filename
                        json_geo['bit_depth'] = bit_depth
                        json_geo['channel_count'] = channel_count
                        # json_output_data[item_key][json_geo_index] = save_output_file(output_path, '{0}_Volume{1}'.format(json_geo_index, output_index),json_geo)
                        json_img_index = 'Img_{0}'.format(geo_index)
                        json_output_data[item_key][json_img_index] = json_geo['volume_file']
                        if io_mode == 1:
                            json_geo['attribs_filename'] = ''
                            json_output_data[item_key][json_geo_index] = save_output_file(output_path,'{0}_Volume{1}'.format(json_geo_index,output_index), json_geo)
                        elif io_mode == 2 or io_mode == 3:
                            attr_geo_index = 'Attr_{0}'.format(geo_index)
                            attribs_filename = '{0}_Volume{1}_{2}.attr_raw'.format(json_geo_index, output_index, datetime.datetime.now().strftime("%y%m%d_%H%M%S"))
                            json_geo['attribs_filename'] = attribs_filename
                            abs_attribs_filename = os.path.join(work_path, attribs_filename)
                            write_attribs_to_file(abs_attribs_filename, json_geo)
                            json_output_data[item_key][json_geo_index] = save_output_file(output_path,'{0}_Volume{1}'.format(json_geo_index,output_index), json_geo)
                            json_output_data[item_key][attr_geo_index] = attribs_filename

                    packed_volume = np.reshape(np.asarray(volume), (xsize, ysize))
                    delay_volume_dict[channel] = packed_volume

                bit_depth = delay_volume_dict['bit_depth']
                numpy_type, bit_scale, is_integer = bit_depth_remap[bit_depth]
                round_wrapper = None
                if is_integer:
                    round_wrapper = lambda x: round(x)
                else:
                    round_wrapper = lambda x: x
                combined_volume = None
                if channel_count == 1:
                    r = np.vectorize(lambda x: numpy_type(round_wrapper(x * bit_scale)))(delay_volume_dict['r'])

                    combined_volume = r
                elif channel_count == 2:
                    r = np.vectorize(lambda x: numpy_type(round_wrapper(x * bit_scale)))(delay_volume_dict['r'])
                    g = np.vectorize(lambda x: numpy_type(round_wrapper(x * bit_scale)))(delay_volume_dict['g'])

                    combined_volume = np.dstack((r, g))
                elif channel_count == 3:
                    r = np.vectorize(lambda x: numpy_type(round_wrapper(x * bit_scale)))(delay_volume_dict['r'])
                    g = np.vectorize(lambda x: numpy_type(round_wrapper(x * bit_scale)))(delay_volume_dict['g'])
                    b = np.vectorize(lambda x: numpy_type(round_wrapper(x * bit_scale)))(delay_volume_dict['b'])

                    combined_volume = np.dstack((r, g, b))
                elif channel_count == 4:
                    r = np.vectorize(lambda x: numpy_type(round_wrapper(x * bit_scale)))(delay_volume_dict['r'])
                    g = np.vectorize(lambda x: numpy_type(round_wrapper(x * bit_scale)))(delay_volume_dict['g'])
                    b = np.vectorize(lambda x: numpy_type(round_wrapper(x * bit_scale)))(delay_volume_dict['b'])
                    a = np.vectorize(lambda x: numpy_type(round_wrapper(x * bit_scale)))(delay_volume_dict['a'])

                    combined_volume = np.dstack((r, g, b, a))
                if raw_compress:
                    with open(save_path, 'ab+') as f_volume:
                        buffer = combined_volume.tobytes()
                        compress_buffer = zlib.compress(buffer)
                        f_volume.write(compress_buffer)
                else:
                    combined_volume.tofile(save_path)

    # handle point data only.
    for input_point_group in input_point_groups:
        if hou.updateProgressAndCheckForInterrupt():
            break
        group_name = ''
        if hasattr(input_point_group, 'name'):
            group_name = input_point_group.name()
        points = input_point_group.points()
        output_index = -1
        if len(points) > 0:
            output_index = points[0].attribValue('output_index')
        else:
            pass

        if output_index < 0:
            continue
        for item_key, item_value in json_output_data.items():
            if hou.updateProgressAndCheckForInterrupt():
                break
            # kivlin, use next_output to add custom output_index:
            if is_output_index_match(output_index, item_value) is False:
                continue
            if 'Curve' in item_value['label']:
                if output_index not in remove_redudant_sets['Curve']:
                    remove_redudant_sets['Curve'].append(output_index)
                    remove_redundant_keys(json_output_data[item_key])
                json_geo = {}
                base_save_to_json([], points, json_geo, 'Curve', geo, group_name)
                geo_index += 1
                json_geo_index = 'Geo_{0}'.format(geo_index)
                if io_mode == 1:
                    json_geo['attribs_filename'] = ''
                    json_output_data[item_key][json_geo_index] = save_output_file(output_path, '{0}_Curve{1}'.format(json_geo_index, output_index), json_geo)
                elif io_mode == 2 or io_mode == 3:
                    attr_geo_index = 'Attr_{0}'.format(geo_index)
                    attribs_filename = '{0}_Curve{1}_{2}.attr_raw'.format(json_geo_index, output_index, datetime.datetime.now().strftime("%y%m%d_%H%M%S"))
                    json_geo['attribs_filename'] = attribs_filename
                    abs_attribs_filename = os.path.join(work_path, attribs_filename)
                    write_attribs_to_file(abs_attribs_filename, json_geo)
                    json_output_data[item_key][json_geo_index] = save_output_file(output_path, '{0}_Curve{1}'.format(json_geo_index, output_index), json_geo)
                    json_output_data[item_key][attr_geo_index] = attribs_filename
            elif 'Instance' in item_value['label']:
                if output_index not in remove_redudant_sets['Instance']:
                    remove_redudant_sets['Instance'].append(output_index)
                    remove_redundant_keys(json_output_data[item_key])
                json_geo = {}
                base_save_to_json([], points, json_geo, 'Instance', geo, group_name)
                # mesh geo
                mesh_geo = None

                geo_index += 1
                json_geo_index = 'Geo_{0}'.format(geo_index)
                if io_mode == 1:
                    json_geo['attribs_filename'] = ''
                    json_output_data[item_key][json_geo_index] = save_output_file(output_path, '{0}_Instance{1}'.format(json_geo_index, output_index), json_geo)
                elif io_mode == 2 or io_mode == 3:
                    attr_geo_index = 'Attr_{0}'.format(geo_index)
                    attribs_filename = '{0}_Instance{1}_{2}.attr_raw'.format(json_geo_index, output_index, datetime.datetime.now().strftime("%y%m%d_%H%M%S"))
                    json_geo['attribs_filename'] = attribs_filename
                    abs_attribs_filename = os.path.join(work_path, attribs_filename)
                    offset = write_attribs_to_file(abs_attribs_filename, json_geo)
                    # mesh geo
                    if mesh_geo is not None:
                        pass
                    json_output_data[item_key][json_geo_index] = save_output_file(output_path, '{0}_Instance{1}'.format(json_geo_index, output_index), json_geo)
                    json_output_data[item_key][attr_geo_index] = attribs_filename

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



def write_attribs_to_file(attribs_filename, json_geo, current_offset = 0):
    attribs = json_geo['attribs']
    attribs_domain_list = [attribs['vertex'], attribs['point'],  attribs['prim'], attribs['detail']]
    with open(os.path.join(work_path, attribs_filename), 'ab+') as f:
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
                elif np.issubdtype(np_type, np.string_) or np.issubdtype(np_type, np.str_) or np.issubdtype(np_type, np.unicode_):
                    data_type = 's'
                    buffer = json.dumps(data.tolist()).encode('utf-8') # @highyang
                else:
                    raise hou.NodeError('write_attribs_to_file error: name: {0}, type: {1}, channel_count: {2}'.format(attrib_name, np_type, channel_count))
                compress_buffer = zlib.compress(buffer)
                f.write(compress_buffer)
                attr_info['data_type'] = data_type
                attr_info['length'] = len(compress_buffer)
                attr_info['raw_length'] = len(buffer)
                current_offset += attr_info['length']
    return current_offset
# step 1. load pson
if len(pson_filename) > 0 and len(work_path) > 0:
    pson_filehandle = open(pson_filename)
    pson = json.load(pson_filehandle)
    pson_filehandle.close()
    # step 1.1. check NEXTPCG_INPUT or NEXTPCG_OUTPUT
    if 'NextPCG_INPUT' in pson:
        pson = pson['NextPCG_INPUT']
    elif 'NextPCG_OUTPUT' in pson:
        pson = pson['NextPCG_OUTPUT']

    json_data = pson

    if 'io_mode' in json_data:
        io_mode = int(json_data['io_mode'])
    if 'raw_compress' in json_data:
        raw_compress = bool(json_data['raw_compress'])

    input_prim_groups = []
    input_point_groups = []
    inputs = node.inputs()
    if len(inputs) >= 0:
        input_geo = inputs[0].geometry()
        input_prim_groups = input_geo.primGroups()
        input_point_groups = input_geo.pointGroups()
        # if len(input_prim_groups) == 0: # if no prim groups or no prim, all the geo as one prim group.
        #    input_prim_groups = [input_geo]

    if len(input_prim_groups) > 0 or len(input_point_groups) > 0:
        for json_key, json_value in json_data.items():
            if '.hda' in json_key:
                if 'Outputs' in json_data[json_key]:
                    json_output_data = json_data[json_key]['Outputs']
                get_to_output_info(input_prim_groups, input_point_groups, work_path, json_output_data)

    output_pson_data = json_data
    # output_pson_path = pson_filename + 'output_pson.pson'
    output_pson_path = pson_filename
    with open(output_pson_path, "w+") as f:
        json.dump(output_pson_data, f)

