# -*- coding: utf-8 -*-
import os
import threading
import asyncio
import subprocess
from typing import Dict

from .meta_helper import Singleton
from .dson import DsonMetaInfo
from .plugin_protocol import server_check_done


class DsonPlugin:
    """An asyncapp

        for each application.
        """
    def __init__(self, name, proc, lock, idx=-1):
        self.name = name
        self.proc = proc
        self.lock = lock
        self.idx = idx

    def __eq__(self, other):
        return self.name == other.name and (self.idx == other.idx or self.idx == -1 or other.idx == -1)


class DsonPool(metaclass=Singleton):
    """An asyncpool

    maintain connection to plugins,
    dispatch task to the plugin
    resolve thread race
    """

    def __init__(self, plugin_max, worker_count, max_task_time, logger):
        """initialize the pool
        
        Args:
            plugin_count (int): number of max plugin running.
            max_task_time (int): max running time of a plugin per task
        """
        self._plugins = {}
        self._plugin_start_times = 0
        self._locks: Dict[str, asyncio.Lock] = {}
        self._lock_create_lock = threading.Lock()
        self._plugin_max = plugin_max
        self._worker_count = worker_count
        self._loop = asyncio.new_event_loop()
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self._max_task_time = max_task_time
        self._workers = None
        self.logger = logger
        self.dson_script_name = ''
        if os.name == 'posix':
            self.dson_script_name = 'dson_init.sh'
        else:
            self.dson_script_name = 'dson_init.bat'

    def run_task_consumer_on_background(self):
        """run task consumer on background thread"""
        t = threading.Thread(name='dson_plugin_pool', target=self.__loop_in_thread,
                             args=(self._loop, self.run_on_task_producer_async(None)))
        t.start()

    @property
    def plugin_start_times(self):
        self._plugin_start_times += 1
        return self._plugin_start_times

    def enqueue_task(self, task, json_error_data, *args):
        """enqueue a session task into session pool
        
        Args:
            task (func): a plugin task to run
            json_error_data: error data used by dson
            *args: arguments pass to this task
        """
        event = threading.Event()
        self.logger.debug(f'enqueue task {task} with param {args}')
        self._loop.call_soon_threadsafe(self.task_queue.put_nowait, (event, task, json_error_data, *args))
        return event

    def __loop_in_thread(self, loop, task):
        asyncio.set_event_loop(loop)
        self.task_queue = asyncio.Queue()
        loop.run_until_complete(task)

    async def run_on_task_producer_async(self, producer):
        """run a task producer and consuming task with plugin pool async

        """
        # work thread run one by one
        self._workers = [asyncio.create_task(self.__worker_loop(i)) for i in range(self._worker_count)]
        
        if producer is None:
            await asyncio.gather(*self._workers, return_exceptions=False)
        else:
            task_producer = asyncio.create_task(producer())
            await asyncio.gather(*self._workers, task_producer, return_exceptions=True)

    async def __worker_loop(self, i):
        """a consumer worker per python plugin session
        ref: https://github.com/CaliDog/asyncpool

        Args:
            i (int): id of python worker
        """
        while True:
            got_obj = False
            got_exception = True
            json_error_data = {}

            try:
                event, task_to_proceed, json_error_data, *args = await self.task_queue.get()
                got_obj = True

                # get or pull the plugin
                # args[0] should be a DsonMetaInfo
                plugin = await self.get_plugin(args[0])
                # plugin lock
                await plugin.lock.acquire()
                running_coro = asyncio.wait_for(task_to_proceed(plugin.proc, *args), self._max_task_time, loop=self._loop)
                await running_coro

                got_exception = False
            except asyncio.CancelledError as e:
                self.logger.info(f'Worker {i} is Cancelled')
                json_error_data['Error_Tag'] = 'CancelledError'
                json_error_data['Error_Info'] = str(e)
                break
            except asyncio.TimeoutError as e:
                json_error_data['Error_Tag'] = 'TimeoutError'
                json_error_data['Error_Info'] = f'plugin time out, max task time {self._max_task_time}'
                self.logger.warning(f'plugin time out, max task time {self._max_task_time}')
            except KeyboardInterrupt as e:
                self.logger.info(f"Worker {i} is Interrupt")
                json_error_data['Error_Tag'] = 'KeyboardInterrupt'
                json_error_data['Error_Info'] = str(e)
                break
            except (MemoryError, SystemError) as e:
                self.logger.exception(e)
                json_error_data['Error_Tag'] = 'MemoryError Or SystemError'
                json_error_data['Error_Info'] = str(e)
                raise
            except ProcessLookupError as e:
                json_error_data['Error_Tag'] = 'ProcessLookupError'
                json_error_data['Error_Info'] = str(e)
                self.logger.exception(e)
            except BaseException as e:
                self.logger.exception(f"Worker {i} Call Failed because {str(e)}")
                json_error_data['Error_Tag'] = 'Error'
                json_error_data['Error_Info'] = str(e)
            finally:
                if got_obj:
                    # inform that task is done
                    event.set()
                    self.task_queue.task_done()
                if got_exception:
                    # if exception, del the plugin in case plugin is still running but no one is expecting the result
                    try:
                        self.del_plugin(plugin)
                    except UnboundLocalError as e:
                        # get_plugin may raise error, so plugin is unbound. We don't need to solve this,
                        # plugin deletion should be done by get_plugin() in this case
                        pass
                else:
                    try:
                        plugin.lock.release()
                    except BaseException as e:
                        pass

    async def get_plugin(self, dson_meta_info: DsonMetaInfo):
        # check data
        assert dson_meta_info.if_in_server==False
        plugin_name = dson_meta_info.plugin_name
        if plugin_name == None:
            raise Exception('expect plugin_name get None')
        # add new plugin
        if plugin_name not in self._plugins:
            # amount new plugin
            plugin_path = os.path.join(os.getenv('NEXTPCG_PYTHON_PROJECT_PATH'), plugin_name).replace('\\', '/')
            bash_path = os.path.join(plugin_path, '.nextpcg', self.dson_script_name).replace('\\', '/')
            if os.name == 'posix':
                proc = subprocess.Popen(['bash', bash_path], shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
            else:
                proc = subprocess.Popen([bash_path], shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
            lock = asyncio.Lock()
            plugin = DsonPlugin(plugin_name, proc, lock, self.plugin_start_times)
            # get plugin
            self._plugins[plugin_name] = plugin
            self.logger.info(f'amount new dson plugin: {plugin_name}')
            await lock.acquire()
            try:
                # ensure that await is after inserting proc to _plugins
                await server_check_done(proc, self.logger)
            except BaseException as e:
                self.del_plugin(plugin)
                raise
            finally:
                try:
                    lock.release()
                except RuntimeError as e:
                    # lock not acquired error
                    self.logger.warning(e)
        else:
            # get plugin
            plugin = self._plugins[plugin_name]
            self.logger.info(f'get dson plugin: {plugin_name}')
        return plugin

    def del_plugin(self, plugin):
        try:
            plugin.proc.terminate()
            plugin.lock.release()
        except BaseException as e:
            # maybe lock is already released
            self.logger.exception(e)
            pass
        try:
            if self._plugins[plugin.name] == plugin:
                del self._plugins[plugin.name]
                self.logger.warning(f'plugin {plugin.name} is terminated')
        except KeyError as e:
            # plugin is already deleted
            pass


def DsonTask(task):
    """a decorator for nextpcg python plugin task
    """
    async def wrapper(*args, **kwargs):
        assert isinstance(args[0], subprocess.Popen), f"{task}'s first parameter should be Popen"
        assert isinstance(args[1], DsonMetaInfo), f"{task}'s second parameter should be DsonMetaInfo"
        await task(*args, **kwargs)
    return wrapper