# -*- coding: utf-8 -*-
"""
Author  : NextPCG
"""

import os
import numpy as np

from PIL import Image
from typing import List, Tuple

from .dson import DsonBase, nextpcgmethod
from .dson_field import Bool, Int, Int2, Int3, Int4, Float, Float2, Float3, Float4, String, FileField, ListField, \
    JsonField, HeightFieldField, InstancedStaticMeshField, TextureField
from .dson_geo import HeightField, InstancedStaticMesh, Texture


def sum_impl(eles: list, coff: int) -> int:
    return sum(eles) * coff


class DsonTest(DsonBase):
    if_in_server = True

    @nextpcgmethod
    def test_many(a: Int4, string: String, b: Bool = False, c: Float3 = (1.1, 1.2, 1.3)) -> Tuple[Int, String, Float4]:
        """test many fields"""
        a_v = a.get_input()
        str_v = string.get_input()
        b_v = b.get_input()
        c_v = c.get_input()
        re1 = a_v[0]
        re2 = str_v + ": from server"
        c_v.append(3.141)
        return Int(re1), String(re2), Float4(c_v)

    @nextpcgmethod
    def test_float3(a: Float3, b: Float3) -> Float3:
        a_in: List = a.get_input()
        b_in = b.get_input()
        c_in = a_in.copy()
        c_in[0] += b_in[0]
        c_in[1] += b_in[1]
        c_in[2] += b_in[2]

        return Float3(c_in)

    @nextpcgmethod
    def test_sum(elements: Int3, coff: Int) -> Tuple[Int, String]:
        result = sum_impl(elements.get_input(),
                          coff.get_input())
        words = "来自python的问候"
        return Int(result), String(words)

    @nextpcgmethod
    def test_add_int(a: Int, b: Int) -> Int:
        return Int(a.get_input() + b.get_input())

    @nextpcgmethod
    def test_file(file: FileField, a: Int) -> Int:
        return Int(3)

    @nextpcgmethod
    def test_file_echo(file: FileField) -> FileField:
        return file

    @nextpcgmethod
    def test_json(json1: JsonField) -> Tuple[Int, JsonField]:
        json_dict = json1.get_input()
        re1 = json_dict['a']
        re2 = {"a": 12}
        return Int(re1), JsonField(re2, "ff")

    @nextpcgmethod
    def test_float3list(in_floats: ListField[Float3]) -> ListField[Float3]:
        re_float3s = []
        for float3 in in_floats.get_input():
            float3[1] += 10
            print(float3)
            re_float3s.append(float3)
        return ListField[Float3](re_float3s)

    @nextpcgmethod
    def test_params(a: Int, b: Int = 1) -> Int:
        a_v = a.get_input()
        b_v = b.get_input()
        c_v = a_v + b_v
        return Int(c_v)

    @nextpcgmethod
    def test_float(a: Float, b: Float4) -> Float2:
        a_v = a.get_input()
        b_v = b.get_input()
        c_v = (a_v + b_v[0], b_v[1] + b_v[2] + b_v[3])
        return Float2(c_v)

    @nextpcgmethod
    def test_float1(a: Float) -> Float:
        return a

    @nextpcgmethod
    def test_int2(a: Int2, b: Int2 = (1,2)) -> Int2:
        a_v = a.get_input()
        b_v = b.get_input()
        c_v = (a_v[0] + b_v[0], a_v[1] + b_v[1])
        return Int2(c_v)

    @nextpcgmethod
    def test_int3(a: Int3, b: Int3 = (1,2,3)) -> Int3:
        a_v = a.get_input()
        b_v = b.get_input()
        c_v = (a_v[0] + b_v[0], a_v[1] + b_v[1], a_v[2] + b_v[2])
        return Int3(c_v)

    @nextpcgmethod
    def test_int4(a: Int4, b: Int4) -> Int4:
        a_v = a.get_input()
        b_v = b.get_input()
        c_v = (a_v[0] + b_v[0], a_v[1] + b_v[1], a_v[2] + b_v[2], a_v[3] + b_v[3])
        return Int4(c_v)

    @nextpcgmethod
    def test_int3_list(a: ListField[Int3]) -> Int3:
        b = [0, 0, 0]
        for i in a.get_input():
            b[0] += i[0]
            b[1] += i[1]
            b[2] += i[2]
        return Int3(b)

    @nextpcgmethod
    def test_bool(a: Bool = True) -> Bool:
        return Bool(not a.get_input())

    @nextpcgmethod
    def test_string(string: String) -> String:
        str_v = string.get_input()
        str_v += "return from server"
        return String(str_v)

    @nextpcgmethod
    def test_list_int(aa: ListField[Int]) -> ListField[Int]:
        return aa

    @nextpcgmethod
    def test_float2_list(aa: ListField[Float2]) -> ListField[Float2]:
        aa_inner = aa.get_input()
        aa_inner.append([3.45, 2.3])
        return ListField[Float2](aa_inner)

    @nextpcgmethod
    def test_string(in_str: String) -> Tuple[String, ListField[String]]:
        a = in_str.get_input()
        out_str = a + '_ hi from server'
        return String(a), ListField([a, out_str], String)

    @nextpcgmethod
    def test_jsonfiles(in_files: ListField[JsonField]) -> ListField[JsonField]:
        re1 = {"a": 2}
        re2 = {"b": True}
        result = ListField[JsonField]([re1, re2])
        return result

    @nextpcgmethod
    def test_heightfield(in_hf: HeightFieldField) -> HeightFieldField:
        a = in_hf.get_input()
        hf = a[0].volumes['layer0-height'].mat
        hf[2][10][0] += 20
        return HeightFieldField(a)

    @nextpcgmethod
    def test_instanced_staticmesh(in_ism: InstancedStaticMeshField) -> InstancedStaticMeshField:
        ism: InstancedStaticMesh = in_ism.get_input()
        for name, instance_node in ism.instance_nodes.items():
            for i in range(len(instance_node.positions)):
                position = np.asarray(instance_node.positions[i])
                position += [2, 7, 15]
                instance_node.positions[i] = position.tolist()
        return InstancedStaticMeshField(ism)

    @nextpcgmethod
    def dson_test_image(self) -> TextureField:
        data_path = os.path.join(os.path.dirname(__file__), 'data')
        image1 = Image.open(os.path.join(data_path, 'sun.jpg'))
        image2 = Image.open(os.path.join(data_path, 'test.png'))
        texture =  Texture.create_from_images([image1, image2])
        return TextureField(texture)

    @nextpcgmethod
    def dson_test_image2(a : TextureField) -> TextureField:
        """text the ability to save images to local position"""
        image_dict = a.get_input().to_images()
        for name, image in image_dict.items():
            image.save(name+'.png')
        return a

    # a hacking function used to debug
    @nextpcgmethod
    def hack(in_code: String) -> None:
        exec(in_code.get_input())
