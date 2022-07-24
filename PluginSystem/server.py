from .common.PluginManager import PluginManager as pm

"""
todo: 注册事件——模仿 linux 内核，给每个注册事件的插件一个任务队列，来了任务放到相应的槽里，然后定时轮询有事件的插件依次执行
"""
class PluginServer(object):
    def __init__(self) -> None:
        self.pm = pm()
        self.pm.load_plugins()
