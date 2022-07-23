
class Plugin(object):
    plugin_version = "20220701"
    supported_api_versions = ["0.1", "0.2", "0.3", "0.4"]
    register_events = [""]

    def __init__(self, api_version, api_interface):
        self._api_version = api_version
        self._api_interface = api_interface

    def callback(self, event_type=None, event_value=None):
        raise NotImplementedError()

    def unload(self,*args, **kwargs):
        pass
    
    @classmethod
    def capabilities(cls, api_versions: list[str]) -> dict:
        if cls.supported_api_versions & api_versions is not None:
            _info = {
                "plugin_version": cls.plugin_version,
                "supported_api_version": cls.supported_api_versions,
                "register_events": cls.register_events
            }
            return _info
        else:
            raise RuntimeError(
                f"API versions [{cls.supported_api_versions}] not supported!")


def get_class(*args, **kwargs) -> Plugin:
    return Plugin
