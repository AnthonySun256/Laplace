from .common.PluginManager import PluginManager as pm
from concurrent.futures import ThreadPoolExecutor
from queue import Queue, Empty
from threading import Thread
import time
"""
TODO: 注册事件——模仿 linux 内核，给每个注册事件的插件一个任务队列，来了任务放到相应的槽里，然后定时轮询有事件的插件依次执行
"""


class PluginServer(object):
    works_num = 4
    queue_size = -1  # infinite

    def __init__(self,Plugin_path="./Plugins") -> None:
        self._pm = pm()
        self._pool = ThreadPoolExecutor(self.works_num)
        self._event_queue = Queue(self.queue_size)
        self._event_list = {"load": [], "command": []}  # example event
        self._plugins = {}
        self._plugin_path = Plugin_path
        self._polling_timer = Thread(target=self._polling_events)
        self._polling_timer.daemon=True
        self._register_plugins()
        self._polling_timer.start()

    def _register_plugins(self):
        """
        Register plugins' instance and events
        TODO:   This part of code is a pice of shit,
                science the data structure I used was not good enough.
                I need to learn something about linux kernel, I believe they
                have a perfect realization
        """
        self._pm.load_plugins(path=self._plugin_path)
        _names = self._pm.get_all_plugin_name()
        self._pm.api.LogTool.debug(f"Loaded plugins:{_names}")
        for _name in _names:
            self._register_plugin(_name)

    def _register_plugin(self, name):
        """Register single plugin.

        Args:
            name (str): plugin name
        """
        self._plugins[name]={}
        self._plugins[name]["instance"] = self._pm.get_plugin_instance(name)
        for event in self._pm.get_plugin_events(name):
            if event in self._event_list:
                self._event_list[event].append(name)
                self._pm.api.LogTool.debug(
                    f"Plugin [{name}] registe event [{event}]")
            else:
                self._pm.api.LogTool.warning(
                    f"Plugin [{name}] want to register not supported event [{event}], skip.")

    def _polling_events(self):
        """
        polling every event in the event queue
        TODO:   Fuck me, this code is too inefficient! 
                This code can be used, but it is not good enough.
                I thought I need some coroutine stuff (For there may many I/O operate)
                (Thank to GIL, I can not really implement multithreading)
                And I did not consider that the plugin may prevented the event from continuing to pass
        """
        while True:
            while not self._event_queue.empty():
                try:
                    _event = self._event_queue.get_nowait()
                    _event_type, _event_value = _event
                    self._exec_plugin_callback(_event_type, _event_value)
                except Empty:
                    pass
            time.sleep(0.5)

    def _exec_plugin_callback(self, event_type, event_value):
        for _plugin_name in self._event_list[event_type]:
            self._pool.submit(
                self._plugins[_plugin_name]["instance"].callback, event_type, event_value)

            self._pm.api.LogTool.debug(
                f"Plugin [{_plugin_name}]] recieved event [{event_type}]")

    def append_event(self, event_type, event_value = None):
        """Add events to event list

        Args:
            event_type (_type_): _description_
            event_value (_type_, optional): _description_. Defaults to None.
        """
        if event_type in self._event_list:
            self._event_queue.put((event_type, event_value), block=False)
            self._pm.api.LogTool.debug(f"Add event [{event_type}],value [{event_value}]")
        else:
            self._pm.api.LogTool.warning(f"Not support event type: [{event_type}]", )
