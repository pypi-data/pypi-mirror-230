# -*- coding: utf-8 -*-
"""simple protocol for dispatch to user defined plugin
Author  : NextPCG
"""

import os
import json
import logging
import threading
import asyncio
from concurrent.futures import Future, ThreadPoolExecutor

# magic code
PROTOCOL_DONE = "s8xc32ds5f"


def module_send_done():
    print(PROTOCOL_DONE)


def setup_logger(logger, logger_path):
    logFormatter = logging.Formatter('%(levelname)s:%(name)s:[%(asctime)s]: %(message)s')

    if not os.path.exists(logger_path):
        os.makedirs(logger_path)

    logfile_path = os.path.join(logger_path, 'nextpcgpython.log')
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


async def server_check_done(proc, logger):
    """check whether task is done
    
    Args:
        proc(subprocess.Popen): process running dson_main.py """
    a = await run_as_daemon(proc.stdout.readline)
    while not PROTOCOL_DONE in a:
        if not a:
            # check if proc is dead
            if proc.poll() is not None:
                # proc is terminated
                raise ProcessLookupError("subprocess is terminated by unknown bug")
        logger.info(a)
        a = await run_as_daemon(proc.stdout.readline)


def server_send_dson(dson_data, work_path, proc):
    json_data_temp_name = os.path.join(work_path, "temp.json").replace('\\','/')
    if not os.path.exists(work_path):
        os.makedirs(work_path, exist_ok=True)
    with open(json_data_temp_name, "w", encoding="utf-8") as f:
        json.dump(dson_data, f)
    proc.stdin.write(json_data_temp_name + " " + work_path + "\n")
    proc.stdin.flush()


def server_load_dson(work_path):
    dson_error_data = {}
    json_data_temp_name = os.path.join(work_path, "temp.json").replace('\\','/')
    with open(json_data_temp_name, "r", encoding='utf-8') as f:
        dson_data = json.load(f)
    json_error_data_name = os.path.join(work_path, 'error.json').replace('\\','/')
    if os.path.exists(json_error_data_name):
        with open(json_error_data_name, 'r', encoding='utf-8') as f:
            dson_error_data = json.load(f)
    return dson_data, dson_error_data


async def run_as_daemon(func, *args):
    future = Future()
    future.set_running_or_notify_cancel()

    def daemon():
        try:
            result = func(*args)
        except Exception as e:
            future.set_exception(e)
        except BaseException as e:
            future.set_exception(e)
        else:
            future.set_result(result)
    
    threading.Thread(target=daemon, daemon=True).start()
    return await asyncio.wrap_future(future)