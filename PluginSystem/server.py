from .common.PluginManager import PluginManager as pm
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
from threading import Thread

"""
TODO: 注册事件——模仿 linux 内核，给每个注册事件的插件一个任务队列，来了任务放到相应的槽里，然后定时轮询有事件的插件依次执行
"""


class PluginServer(object):
    works_num = 4
    queue_size = 0  # infinite

    def __init__(self) -> None:
        self._pm = pm()
        self._pool = ThreadPoolExecutor(self.works_num)
        self._event_queue = Queue(0)
        self._event_list = {"load": [], "command": []}  # example event
        self._plugins = {}

    # def _update_events(self, event_type, event_value):
    #     raise NotImplementedError

    def _register_plugins(self):
        """
        Register plugins' instance and events
        TODO:   This part of code is a pice of shit,
                science the data structure I used was not good enough.
                I need to learn something about linux kernel, I believe they
                have a perfect realization
        """
        self._pm.load_plugins()
        _names = self._pm.get_all_plugin_name()
        for _name in _names:
            self._plugins[_name]["instance"] = self._pm.get_plugin(_name)
            for event in self._pm.get_plugin_events(_name):
                if event in self._event_list:
                    self._event_list[event].append(_name)

    def _polling_events(self):
        """
        polling every event in the event queue
        TODO:   Fuck me, this code is too inefficient! 
                This code can be used, but it is not good enough.
                I thought I need some coroutine stuff (For there may many I/O operate)
                (Thank to GIL, I can not really implement multithreading)
                And I did not consider that the plugin may prevented the event from continuing to pass
        """
        raise NotImplementedError()

    def sent_event(self, event_type, event_value):
        if event_type in self._event_list:
            self._event_queue.put(tuple(event_type, event_value))
