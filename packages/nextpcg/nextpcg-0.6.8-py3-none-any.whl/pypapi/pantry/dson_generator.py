import json
import yaml
import os, sys
from pypapi import *

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
base_path = os.path.dirname(__file__)

# read dson_config.yaml
dson_config = {}
with open(os.path.join(base_path, 'dson_config.yaml'), 'r', encoding='utf-8') as f:
    dson_config = yaml.safe_load(f.read())
dson_plugin_name = dson_config['name']

# get all dson class
for module in dson_config['modules']:
    if isinstance(module, str):
        # only module name
        try:
            __import__(module, globals(), locals(), [], 0)
        except Exception as e:
            print(e)
            exit(1)
    else:
        for module_name in module:
            # if has class name
            try:
                __import__(module_name, globals(), locals(), module[module_name], 0)
            except Exception as e:
                print(e)
                exit(1)


def generate_dson_files(plugin_name, dson_path):
    index = 0
    if not os.path.exists(dson_path):
        os.makedirs(dson_path, exist_ok=True)
    for cls_name, cls in DsonManager().dsonMap.items():
        for name, value in vars(cls).items():
            if isinstance(value, nextpcgmethod):
                func = value.__func__
                dson_meta_info = DsonMetaInfo(cls_name, cls.if_in_server, plugin_name)
                json_data = create_dson_from_pda(func, cls.label, dson_meta_info)
                file_name = name + '.dson'
                file_path = os.path.join(dson_path, file_name).replace('\\', '/')
                fp = open(file_path, "w")
                json.dump(json_data, fp)
                index += 1


def generate_dson_init_script(nextpcg_path, conda_env):
    if os.name != 'posix':
        # windows
        script_name = 'dson_init.bat'
        script_string = f"""@echo off
cd %~dp0 
cd ..
call conda activate {conda_env}
@REM call conda env list
python dson_main.py
"""
    else:
        # linux
        script_name = 'dson_init.sh'
        script_string = f"""#! /usr/bin/bash
source ~/.bash_profile # get conda into env
BASEDIR=$(dirname $(readlink -f "$0"))
cd "$BASEDIR"
cd ..
eval "$(conda shell.bash hook)"
conda activate {conda_env}
python dson_main.py
"""
    if not os.path.exists(nextpcg_path):
        os.makedirs(nextpcg_path, exist_ok=True)
    with open(os.path.join(nextpcg_path, script_name), 'w', encoding='utf-8') as f:
        f.write(script_string)


def generate_dson_main(base_path, dson_config):
    dsonmain_string1 ="""from pypapi import Dispatcher
from pypapi.plugin_protocol import module_send_done
import sys
import os
import json
import logging

"""
    # dsonmain_import contains code used to load necessary modules or classes
    dsonmain_import =''
    for module in dson_config['modules']:
        if isinstance(module, str):
            # only module name
            try:
                dsonmain_import+='import ' + module + '\n'
            except Exception as e:
                print(e)
                exit(1)
        else:
            for module_name in module:
                # if has class name
                dsonmain_import += 'from ' + module_name + ' import  '
                for class_name in module[module_name]:
                    dsonmain_import += class_name +','
                dsonmain_import = dsonmain_import[:-1]
    dsonmain_string2 = f"""

dson_plugin_name = '{dson_plugin_name}'
dispatcher = Dispatcher()
logger = logging.getLogger('pypapi_'+dson_plugin_name)
current_path = os.path.split(os.path.realpath(__file__))[0] # path to dosn_path.py
dot_nextpcg_path = os.path.join(current_path, '.nextpcg')

def set_up_logger():
    logFormatter = logging.Formatter('%(levelname)s:%(name)s:[%(asctime)s]: %(message)s')

    if not os.path.exists(dot_nextpcg_path):
        os.makedirs(dot_nextpcg_path)

    logfile_path = os.path.join(current_path, '.nextpcg', 'nextpcgpython.log')
    # delete old log file
    try:
        os.remove(logfile_path)
    except OSError:
        pass

    fileHandler = logging.FileHandler(logfile_path)
    fileHandler.setFormatter(logFormatter)

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)

    logger.addHandler(fileHandler)
    logger.addHandler(consoleHandler)
    
class Tee:
    def __init__(self, *files):
        self.files = files
    
    def write(self, obj):
        for f in self.files:
            f.write(obj)
            f.flush()
    
    def flush(self):
        for f in self.files:
            f.flush()

if __name__ == '__main__':
    set_up_logger()
    ferr = open(os.path.join(dot_nextpcg_path, 'err.txt'), 'w')
    sys.stderr = Tee(sys.stderr,ferr)
    module_send_done()
    while(True):
        json_file_name, work_path = input().split()
        json_error_data = {{}}
        try:
            with open(json_file_name, 'r') as f:
                json_data = json.load(f)
            if not json_data:
                print("didn't get dson data")
                module_send_done()
            dispatcher.run_func(json_data, logger, work_path, json_error_data)
            json_data_error_file_name = os.path.join(work_path, 'error.json').replace("\\\\",'/')
            # write back json_data
            with open(json_file_name, 'w') as f:
                json.dump(json_data, f)
        except Exception as e:
            json_error_data['Error_Tag'] = 'plugin {dson_plugin_name} error in main loop'
            json_error_data['Error_Info'] = str(e)
            logger.exception(e)
        finally:
            with open(json_data_error_file_name, 'w') as f:
                json_error_data = json.dump(json_error_data, f)
        module_send_done()
"""
    dsonmain_string = dsonmain_string1 + dsonmain_import + dsonmain_string2
    with open(os.path.join(base_path, 'dson_main.py'), 'w', encoding='utf-8') as f:
        f.write(dsonmain_string)



if __name__ == "__main__":
    try:
        dson_path = os.path.join(base_path, "dson")
        nextpcg_path = os.path.join(base_path, '.nextpcg')
        generate_dson_files(dson_plugin_name, dson_path)
        generate_dson_init_script(nextpcg_path, dson_config['conda_env'])
        generate_dson_main(base_path, dson_config)        
    except Exception as e:
        print(e)
        exit(1) 
    # todo:  generate dson_main, dson_init.bat, dson_init.sh
    