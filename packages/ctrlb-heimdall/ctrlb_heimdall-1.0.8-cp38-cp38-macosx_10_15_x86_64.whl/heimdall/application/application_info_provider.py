import abc, sys

from heimdall.config import config_names
from heimdall.config.config_provider import ConfigProvider

ABC = abc.ABCMeta('ABC', (object,), {})

"""
This is a base class. 
Implemented by config_aware_application_info_provider
"""
class ApplicationInfoProvider(ABC):
    
    APPLICATION_RUNTIME = "python"
    APPLICATION_RUNTIME_VERSION = str(sys.version_info[0])

    @abc.abstractmethod
    def get_application_info(self):
        pass

    @staticmethod
    def parse_application_tags():
        application_tags = {}
        prefix_length = len(config_names.ATLAS_APPLICATION_TAG_PREFIX)
        for key in ConfigProvider.configs:
            if key.startswith(config_names.ATLAS_APPLICATION_TAG_PREFIX):
                app_tag_key = key[prefix_length:]
                val = ConfigProvider.get(key)
                application_tags[app_tag_key] = val
        return application_tags
