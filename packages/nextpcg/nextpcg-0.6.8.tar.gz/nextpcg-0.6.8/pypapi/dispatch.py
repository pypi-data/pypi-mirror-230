# -*- coding: utf-8 -*-
"""
Author  : NextPCG
"""

import os
import logging
from typing import Dict, List, Union, Tuple

from .const import *
from .dson import DsonMetaInfo, DsonManager
from .dson_field import FieldManager, Field, FieldDesc
from .meta_helper import Singleton


class Dispatcher(metaclass=Singleton):
    def __init__(self):
        pass

    @staticmethod
    def prepare_inputs(inputs_json: Dict, field_desc: FieldDesc):
        """get inputs from Input:{} json object
        """
        inputs = []
        input_index = 0
        while input_index < len(inputs_json):
            input_index += 1
            input_name = dson_input_tag + str(input_index)
            json_object = inputs_json[dson_input_tag + str(input_index)]
            inputs.append(FieldManager().create_field(json_object, input_name, field_desc))
        return inputs

    @staticmethod
    def prepare_params(params_json: Dict, field_desc: FieldDesc):
        """prepare params from json object in 'Params: {}'
        """
        params = {}
        for name, json_object in params_json.items():
            params[name] = FieldManager().create_field(json_object, name, field_desc)
        return params

    @staticmethod
    def prepare_outputs(outputs_json: Dict, results: Union[Tuple[Field], Field], field_desc: FieldDesc):
        if results is None:
            raise Exception("none results to prepare")
        if isinstance(results, tuple):
            for index in range(len(results)):
                results[index].get_output(outputs_json[dson_output_tag + str(index + 1)], field_desc)
        else:
            results.get_output(outputs_json[dson_output_tag + "1"], field_desc)

    def run_func(self, json_data: Dict, logger: logging.Logger, work_path: str, pson_system_tag: str, json_error_data: Dict):
        """find function in mod and run it

        side effects: change json_data
        """
        # clear error info
        if 'error' in json_data:
            del json_data['error']

        # get raw compress
        raw_compress = False
        if 'raw_compress' in json_data:
            raw_compress = bool(json_data['raw_compress'])

        # get io mode
        io_mode = 1
        if 'io_mode' in json_data:
            io_mode = int(json_data['io_mode'])

        # nextpcg admin report.
        folder = os.path.basename(work_path)
        user = json_data[pson_system_tag]['user']

        # create field_desc
        field_desc = FieldDesc(work_path, io_mode, raw_compress)

        # find dson class
        dson_meta_info = self.get_dson_meta_info(json_data)
        cls_name = dson_meta_info.cls_name
        if cls_name not in DsonManager().dsonMap:
            raise Exception("not known class name: %s" % cls_name)
        mod = DsonManager().dsonMap[cls_name]
        func_tag = mod.label
        for json_key, json_value in json_data.items():
            if func_tag in json_key:
                inputs = []
                try:
                    logger.info("Start handing inputs...")
                    if dson_inputs_tag in json_value:
                        inputs = self.prepare_inputs(json_value[dson_inputs_tag], field_desc)
                    logger.info("Finish handing inputs!")
                except Exception as e:
                    json_error_data['Error_Tag'] = 'dispatcher handing inputs error'
                    json_error_data['Error_Info'] = str(e)
                    logger.exception(e)
                    return
                params = {}
                try:
                    logger.info("Start handing params...")
                    if dson_params_tag in json_value:
                        params = self.prepare_params(json_value[dson_params_tag], field_desc)
                    logger.info("Start handing params!")
                except Exception as e:
                    json_error_data['Error_Tag'] = 'dispatcher handing params error'
                    json_error_data['Error_Info'] = str(e)
                    logger.exception(e)
                    return
                results = None
                try:
                    # exec function
                    logger.info("Start calling functions...")
                    func_name = json_key
                    func_name = func_name.split('.')[0]
                    func = mod.__dict__[func_name].__func__
                    results = func(*inputs, **params)
                    logger.info("Finish calling functions!")
                except Exception as e:
                    json_error_data['Error_Tag'] = 'dispatcher error in running function'
                    json_error_data['Error_Info'] = str(e)
                    logger.exception("running function error")
                    return
                try:
                    # handing outputs
                    logger.info("Start handing outputs...")
                    if dson_outputs_tag in json_value:
                        self.prepare_outputs(json_value[dson_outputs_tag], results, field_desc)
                    logger.info("Finish handing outputs!")
                except Exception as e:
                    json_error_data['Error_Tag'] = 'dispatcher error in handing outputs'
                    json_error_data['Error_Info'] = str(e)
                    logger.exception("error in handing outputs")
                    return

    @staticmethod
    def get_dson_meta_info(json_data):
        return DsonMetaInfo.from_dson(json_data)


# for test
if __name__ == "__main__":
    pass
