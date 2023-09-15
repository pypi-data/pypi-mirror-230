# -*- coding: utf-8 -*-
"""
Author  : NextPCG
"""

import json
import os, sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from .dson import nextpcgmethod, DsonManager, DsonMetaInfo
from .dson_create import create_dson_from_pda

# get all dson class
from pypapi.dson_test import DsonTest
from pypapi.building.building import DsonBuilding
from pypapi.wilderness.wilderness_dson import DsonWildness

dson_path = os.path.join(os.getcwd(), "dson")


if __name__ == "__main__":
    index = 0
    if not os.path.exists(dson_path):
        os.makedirs(dson_path, exist_ok=True)
    for cls_name, cls in DsonManager().dsonMap.items():
        for name, value in vars(cls).items():
            if isinstance(value, nextpcgmethod):
                func = value.__func__
                dson_meta_info = DsonMetaInfo(cls_name, cls.if_in_server)
                json_data = create_dson_from_pda(func, cls.label, dson_meta_info)
                file_name = name + '.dson'
                file_path = os.path.join(dson_path, file_name).replace('\\', '/')
                fp = open(file_path, "w")
                json.dump(json_data, fp)
                index += 1
