from .PluginTemplate import Plugin
import os
import sys
import importlib
import logging


class APIInterface(object):
    def __init__(self, *args, **kwargs):
        self.LogTool = logging
        self.LogTool.basicConfig(level=logging.DEBUG,
                                 format="[%(asctime)s] [%(levelname)s] %(message)s",
                                 datefmt='%Y-%m-%d  %H:%M:%S')


class PluginManager(object):
    provide_api_version = ["0.1", "0.2"]

    def __init__(self) -> None:
        super().__init__()
        self.api = self.create_api_interface()
        self.__plugins = {}

    @classmethod
    def create_api_interface(cls, *args, **kwargs) -> APIInterface:
        return APIInterface(*args, **kwargs)

    def _find_plugins(self, plugin_path:str):
        """
        Find all plugins
        """
        if plugin_path is None:
            self.api.LogTool.critical("Missing arg: [plugin_path]")
            raise RuntimeError("Missing arg plugin_path")

        self.api.LogTool.debug("Now in the path [%s]", os.getcwd())
        for dirname in os.listdir(plugin_path):
            f = os.path.join(plugin_path, dirname, "Plugin.py")
            self.api.LogTool.debug(
                "Find  plugins [%s] in [%s]", os.path.basename(dirname), f)
            if os.path.exists(f):
                _plugin_name = dirname

                if _plugin_name in self.__plugins:
                    self.api.LogTool.warning(
                        "Plugin [%s] already exists, skipping", _plugin_name)
                else:
                    self.__plugins[_plugin_name] = {}
                    self.api.LogTool.info(
                        "Find plugin [%s]", _plugin_name)

    def _load_plugin(self, name):
        if name in self.__plugins:
            _mod = importlib.import_module(
                ".",f"PluginSystem.Plugins.{name}.Plugin")
            try:
                _cls = _mod.get_class()
                _plugin_info = _cls.capabilities(self.provide_api_version)
                self.__plugins[name]["module"] = _cls
                self.__plugins[name]["info"] = _plugin_info
                self.api.LogTool.info("Plugin [%s] Load successful", name)
            except RuntimeError:
                self.api.LogTool.warning(
                    "Incompatible plugin detected [%s]", name)
    
    def get_all_plugin_name(self):
        return self.__plugins.keys

    def remove_plugin(self, name):
        if name in sys.modules:
            sys.modules.pop(name)
            self.api.LogTool.info("Unload plugin [%s]", name)
            self.__plugins[name] = {}
        self.api.LogTool.warning("Plugin [%s] does not be loaded yet", name)

    def get_plugin(self, name):
        _instant = None
        if name in self.__plugins:
            _api_version = self.__plugins[name]["info"]["supported_api_version"]
            _instant = self.__plugins[name]["module"](_api_version, self.api)
            self.api.LogTool.debug("Create a instance of Plugin [%s]", name)

        else:
            self.api.LogTool.warning(
                "Failed to create plugin instance, because plugin [%s] does not exist.", name)

        return _instant

    def load_plugins(self, path="PluginSystem/Plugins"):
        self._find_plugins(path)
        for name in self.__plugins.keys():
            self._load_plugin(name)
