# -*- coding: utf-8 -*-
"""a demo to run houdini server
Author  : Cheneyshen
Email   : cheneyshen@tencent.com
"""

import os
import json
import requests

# log
import logging
logging.basicConfig(level=logging.INFO)

'''
common
'''

if os.name == 'posix':
    # linux default value
    host = '9.134.229.56'
else:
    # windows default value
    host = '127.0.0.1'
port = 5000
'''
Server
'''

root_temp_path = os.path.join(os.getcwd(), 'temp')
root_static_path = os.path.join(os.getcwd(), 'nextpcg_admin_static')
if os.name == 'posix':
    # linux pdg root path
    root_pdg_temp_path = r"/data/HQShared/nextpcg_pdg_temp"
else:
    # windows pdg root path
    root_pdg_temp_path = r"\\9.135.141.42/HQShared/nextpcg_pdg_temp"

label_nextpcg_filename = 'output.json'
label_nextpcg_fileinput = 'NextPCG_INPUT'
label_nextpcg_fileoutput = 'NextPCG_OUTPUT'
label_nextpcg_dbname = 'database'

pson_error_tag = 'error'
pson_system_tag = 'system'

# for houdini
pson_hda_tag = '.hda'
# for terrain
pson_tda_tag = '.tda'
# for python
pson_cda_tag = '.pda'
# for substance
pson_sda_tag = '.sda'

pson_inputs_tag = 'Inputs'
pson_params_tag = 'Params'
pson_outputs_tag = 'Outputs'

label_file_name = 'File Name'
label_file_data = 'File Data'
label_folder_name = 'Folder Name'
label_folder_data = 'Folder Data'


def setup_logger(logger: logging.Logger):
    logger.handlers = [] # remove default handlers
    logger.propagate = False
    # define format
    logFormatter = logging.Formatter('%(levelname)s:%(name)s:[%(asctime)s]: %(message)s')
    # set info
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    consoleHandler.setLevel(logging.DEBUG)
    logger.addHandler(consoleHandler)


def get_param_value(param_val):
    if 'parmTemplateType.Toggle' in param_val['Type']:
        if isinstance(param_val['Value Data'], list):
            tmp_value = True if param_val['Value Data'][0] == "True" else False
            return tmp_value
        else:
            tmp_value = True if param_val['Value Data'] == "True" else False
            return tmp_value
    elif 'parmTemplateType.Menu' in param_val['Type']:
        if isinstance(param_val['Value Data'], list):
            return int(param_val['Value Data'][0])
        else:
            return int(param_val['Value Data'])
    elif 'parmData.Int' in param_val['Data Type']:
        return param_val['Value Data']
    elif 'parmData.Float' in param_val['Data Type']:
        return param_val['Value Data']
    elif 'parmData.String' in param_val['Data Type']:
        if isinstance(param_val['Value Data'], list) and len(param_val['Value Data']) > 1:
            return param_val['Value Data']
        else:
            return str(param_val['Value Data'][0])
    else:
        if isinstance(param_val['Value Data'], list):
            return param_val['Value Data'][0]
        else:
            return str(param_val['Value Data'])


'''
Client
'''

upload_file_url = 'http://' + host + ':5000/UploadFile/'
download_file_url = 'http://' + host + ':5000/DownloadFile/'

houdini_url = 'http://' + host + ':5000/HttpHoudini/'
substance_url = 'http://' + host + ':5000/HttpSubstance/'
terrain_url = 'http://' + host + ':5000/HttpTerrain/'
python_url = 'http://' + host + ':5000/HttpPython/'


def create_temp_store_path(json_data, work_path):
    if pson_system_tag in json_data:
        if 'path' in json_data[pson_system_tag]:
            work_path = os.path.join(work_path, json_data[pson_system_tag]['path']).replace("\\", "/")
            if not os.path.exists(work_path):
                os.makedirs(work_path, exist_ok=True)
        else:
            raise ValueError('No path in pson_system_tag in json file.')
    else:
        raise ValueError('No pson_system_tag in json file.')
    return work_path


def secure_filepath(filename):
    # https://iwiki.woa.com/pages/viewpage.action?pageId=1325302780#macro0_python-3
    if ".." in filename:
        raise ValueError('Illegal path filename:' + filename)


def request_upload(path, filename, file_headers):
    load_path = os.path.join(path, filename).replace("\\", "/")
    upload_file = {'file': open(load_path, "rb")}
    r = requests.post(upload_file_url, headers=file_headers, files=upload_file)
    ########## temp : highyang : fix json bug
    # re_json = json.loads(r.content)['filename']
    # return re_json


def request_upload_folder(path, folder_name, file_headers):
    filenames = []
    file_headers['path'] = os.path.join(file_headers['path'], folder_name)
    for filename in os.listdir(path):
        if os.path.isfile(os.path.join(path, filename)):
            request_upload(path, filename, file_headers)
            filenames.append(filename)
    return filenames


def request_download(path, filename, file_headers):
    download_json = {'filename': filename}
    r_file = requests.post(download_file_url, json=download_json, headers=file_headers)
    if r_file.status_code < 400:
        save_path = os.path.join(path, filename)
        with open(save_path, "wb") as f_tmp:
            f_tmp.write(r_file.content)


def request_download_folder(path, folder_name, file_headers):
    folder_name = os.path.join(file_headers['path'], folder_name)
    download_json = {'foldername': folder_name}
    r_file = requests.post(download_file_url, json=download_json, headers=file_headers)
    if r_file.status_code < 400:
        # create folder
        folder_path = os.path.join(path, folder_name)
        if not os.path.exists(folder_path):
            os.mkdir(folder_path)
        # download files
        r_content = json.loads(r_file.content)
        for file_name in r_content['filelist']:
            request_download(folder_path, file_name, file_headers)


def get_input_file(work_path, json_data, pson_tag):
    send_path = work_path
    upload_file_headers = {'user': 'null', 'path': ''}
    print("File Send...")
    for json_key, json_value in json_data.items():
        if pson_system_tag in json_key:
            # file user
            user = json_data[json_key]['user']
            upload_file_headers['user'] = user
            # file path_send
            send_path = os.path.join(send_path, json_data[json_key]['path_send']).replace("\\", "/")
            print("File Send Path: " + send_path)
    for json_key, json_value in json_data.items():
        if pson_tag in json_key:
            # for each parameter files
            try:
                if pson_params_tag in json_data[json_key]:
                    for param_key, param_val in json_data[json_key][pson_params_tag].items():
                        if 'Tags' in param_val.keys() and 'filechooser_mode' in param_val['Tags']:
                            if 'read' in param_val['Tags']['filechooser_mode']:
                                if label_file_name in param_val.keys():
                                    print("Upload Param File: " + param_val[label_file_name])
                                    param_val[label_file_data] = request_upload(send_path, param_val[label_file_name], upload_file_headers)
                                elif label_folder_name in param_val.keys():
                                    print("Upload Param Folder: " + param_val[label_folder_name])
                                    param_val[label_folder_data] = request_upload_folder(send_path, param_val[label_folder_name], upload_file_headers)
                                else:
                                    print('Notice add {0},{1} tag to input file parameters.'.format(label_file_name, label_folder_name))
            except Exception as e:
                print('Parameter File Send Failed: {0}'.format(e))
                return
            # for each input files
            try:
                if pson_inputs_tag in json_data[json_key]:
                    for input_key, input_val in json_data[json_key][pson_inputs_tag].items():
                        for geo_key, geo_val in json_data[json_key][pson_inputs_tag][input_key].items():
                            if 'Geo_' in geo_key or 'Img_' in geo_key:
                                print("Upload Input File: " + geo_val)
                                request_upload(send_path, geo_val, upload_file_headers)
                            elif 'Attr_' in geo_key:
                                print("Upload Attr File: " + geo_val)
                                request_upload(send_path, geo_val, upload_file_headers)
                            elif 'Folder_' in geo_key:
                                print("Upload Input Folder: " + geo_val)
                                request_upload_folder(send_path, geo_val, upload_file_headers)
            except Exception as e:
                print('Input Files Send Failed: {0}'.format(e))
                return


def handle_output_file(work_path, receive_info, pson_tag):
    receive_path = work_path
    download_file_headers = {'user': 'null', 'path': ''}
    print("File Receive...")
    if receive_info.status_code < 400:
        try:
            json_data_output = json.loads(receive_info.content)
            json_data = json_data_output[label_nextpcg_fileoutput]
            for json_key, json_value in json_data.items():
                if pson_error_tag in json_key:
                    print('Error_Tag: {0}'.format(json_data[pson_error_tag]['Error_Tag']))
                    print('Error_Info: {0}'.format(json_data[pson_error_tag]['Error_Info']))
                    return
            for json_key, json_value in json_data.items():
                if pson_system_tag in json_key:
                    # file user
                    user = json_data[json_key]['user']
                    download_file_headers['user'] = user
                    # file receive_path
                    receive_path = os.path.join(receive_path, json_data[json_key]['path_receive'])
                    print("File Receive Path: " + receive_path)
            for json_key, json_value in json_data.items():
                if pson_tag in json_key:
                    # get parameters files
                    try:
                        if pson_params_tag in json_data[json_key]:
                            for param_key, param_val in json_data[json_key][pson_params_tag].items():
                                if 'Tags' in param_val.keys() and 'filechooser_mode' in param_val['Tags']:
                                    if 'write' in param_val['Tags']['filechooser_mode']:
                                        if label_file_name in param_val.keys():
                                            tmp_filename = param_val[label_file_name]
                                            print("Download Param File: " + tmp_filename)
                                            request_download(receive_path, tmp_filename, download_file_headers)
                                        elif label_folder_name in param_val.keys():
                                            tmp_foldername = param_val[label_folder_name]
                                            print("Download Param Folder: " + tmp_foldername)
                                            request_download_folder(receive_path, tmp_foldername, download_file_headers)
                                        else:
                                            print('Notice add {0} tag to output file parameters.'.format(
                                                label_file_name))
                    except Exception as e:
                        print('Parameter File Receive Failed: {0}'.format(e))
                    # get output files
                    try:
                        if pson_outputs_tag in json_data[json_key]:
                            for output_key, output_val in json_data[json_key][pson_outputs_tag].items():
                                for geo_key, geo_val in json_data[json_key][pson_outputs_tag][output_key].items():
                                    if 'Geo_' in geo_key or 'Img_' in geo_key:
                                        print("Download Output File: " + geo_val)
                                        request_download(receive_path, geo_val, download_file_headers)
                                    elif 'Folder_' in geo_key:
                                        print("Download Output Folder: " + geo_val)
                                        request_download_folder(receive_path, geo_val, download_file_headers)
                    except Exception as e:
                        print('Output File Receive Failed: {0}'.format(e))
                    if pson_hda_tag in json_key:
                        # get hip file
                        hip_filename = json_key.split('.')[0] + ".hip"
                        download_hip_json = {'filename': hip_filename}
                        r_hip = requests.post(download_file_url, json=download_hip_json, headers=download_file_headers)
                        hip_save_path = os.path.join(receive_path, hip_filename)
                        with open(hip_save_path, "wb") as f_hip:
                            f_hip.write(r_hip.content)
            # save output file
            output_save_path = os.path.join(receive_path, 'output.json')
            with open(output_save_path, "wb") as f_output:
                f_output.write(receive_info.content)
        except Exception as e:
            print("Write File Failed: {0}".format(e))
        print("All Finished.")
    else:
        print("SOMETHING UNKNOWN ERROR! \n Please contact cheneyshen@tencent.com \n")


def get_input_file_python(work_path, json_data, pson_tag, path):
    send_path = work_path
    upload_file_headers = {'user': 'null', 'path': ''}
    print("File Send...")
    for json_key, json_value in json_data.items():
        if pson_system_tag in json_key:
            # file user
            user = json_data[json_key]['user']
            upload_file_headers['user'] = user
            upload_file_headers['path_list'] = path
            # file path_send
            send_path = os.path.join(send_path, json_data[json_key]['path_send']).replace("\\", "/")
            print("File Send Path: " + send_path)
    for json_key, json_value in json_data.items():
        if pson_tag in json_key:
            # for each input files
            try:
                if pson_inputs_tag in json_data[json_key]:
                    for input_key, input_val in json_data[json_key][pson_inputs_tag].items():
                        # case jsonfile
                        if "Json" in input_val['Type'] or ('Data Type' in input_val and "Json" in input_val['Data Type']):
                            for json_filename in input_val["Value Data"]:
                                print("Upload JsonFile: " + json_filename)
                                request_upload(send_path, json_filename, upload_file_headers)
                            continue
                        for geo_key, geo_val in json_data[json_key][pson_inputs_tag][input_key].items():
                            if 'Geo_' in geo_key or 'Img_' in geo_key:
                                print("Upload Input File: " + geo_val)
                                request_upload(send_path, geo_val, upload_file_headers)
                            elif 'Attr_' in geo_key:
                                print("Upload Attr File: " + geo_val)
                                request_upload(send_path, geo_val, upload_file_headers)
                            elif 'Folder_' in geo_key:
                                print("Upload Input Folder: " + geo_val)
                                request_upload_folder(send_path, geo_val, upload_file_headers)
            except Exception as e:
                print('Input Files Send Failed: {0}'.format(e))
                return


def handle_output_file_python(work_path, receive_info, pson_tag, index=None):
    receive_path = work_path
    download_file_headers = {'user': 'null', 'path': ''}
    print("File Receive...")
    if receive_info.status_code < 400:
        try:
            json_data_output = json.loads(receive_info.content)
            json_data = json_data_output[label_nextpcg_fileoutput]
            for json_key, json_value in json_data.items():
                if pson_error_tag in json_key:
                    print('Error_Tag: {0}'.format(json_data[pson_error_tag]['Error_Tag']))
                    print('Error_Info: {0}'.format(json_data[pson_error_tag]['Error_Info']))
                    return
            for json_key, json_value in json_data.items():
                if pson_system_tag in json_key:
                    # file user
                    user = json_data[json_key]['user']
                    download_file_headers['user'] = user
                    # file receive_path
                    receive_path = os.path.join(receive_path, json_data[json_key]['path_receive'])
                    print("File Receive Path: " + receive_path)
            for json_key, json_value in json_data.items():
                if pson_tag in json_key:
                    # get output files
                    try:
                        if pson_outputs_tag in json_data[json_key]:
                            for output_key, output_val in json_data[json_key][pson_outputs_tag].items():
                                # case jsonfile
                                if "Json" in output_val['Type'] or ('Data Type' in output_val and "Json" in output_val['Data Type']):
                                    for json_filename in output_val["Value Data"]:
                                        print("Download Output JsonFile: " + json_filename)
                                        request_download(receive_path, json_filename, download_file_headers)
                                for geo_key, geo_val in json_data[json_key][pson_outputs_tag][output_key].items():
                                    if 'Geo_' in geo_key or 'Img_' in geo_key:
                                        print("Download Output File: " + geo_val)
                                        request_download(receive_path, geo_val, download_file_headers)
                                    elif 'Folder_' in geo_key:
                                        print("Download Output Folder: " + geo_val)
                                        request_download_folder(receive_path, geo_val, download_file_headers)
                    except Exception as e:
                        print('Output File Receive Failed: {0}'.format(e))
            # save output file
            output_name = 'output'
            if index is not None:
                output_name+=str(index)
            output_name += '.json'
            output_save_path = os.path.join(receive_path, output_name)
            with open(output_save_path, "wb") as f_output:
                f_output.write(receive_info.content)
        except Exception as e:
            print("Write File Failed: {0}".format(e))
        print("All Finished.")
    else:
        print("SOMETHING UNKNOWN ERROR! \n Please contact cheneyshen@tencent.com \n")
