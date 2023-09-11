import socket
import sys
import uuid

from heimdall.application.application_info_provider import ApplicationInfoProvider
from heimdall.config import config_names
from heimdall.config.config_provider import ConfigProvider


class ConfigAwareApplicationInfoProvider(ApplicationInfoProvider):
    def __init__(self):
        self.applicationInstanceId = ConfigAwareApplicationInfoProvider.get_default_application_instance_id(
                None)
        # self.application_info = ConfigAwareApplicationInfoProvider.get_application_info_from_config()
        # if self.application_info.get('applicationId') is None:
        # self.application_info['applicationId'] = ConfigAwareApplicationInfoProvider.get_default_application_id(
        #     self.application_info['applicationName'])

    def get_application_info(self):
        self.application_info = {
            # 'applicationId': ConfigProvider.get(config_names.ATLAS_APPLICATION_ID),
            'applicationInstanceId': self.applicationInstanceId,
            'applicationDomainName': ConfigProvider.get(config_names.ATLAS_APPLICATION_DOMAIN_NAME, ''),
            'applicationClassName': ConfigProvider.get(config_names.ATLAS_APPLICATION_CLASS_NAME, ''),
            'applicationName': ConfigProvider.get(config_names.ATLAS_APPLICATION_NAME),
            'applicationVersion': ConfigProvider.get(config_names.ATLAS_APPLICATION_VERSION),
            'applicationStage': ConfigProvider.get(config_names.ATLAS_APPLICATION_STAGE),
            'applicationRegion': ConfigProvider.get(config_names.ATLAS_APPLICATION_REGION, ''),
            'applicationRuntime': 'python',
            'applicationRuntimeVersion': str(sys.version_info[0]),
            'applicationTags': ApplicationInfoProvider.parse_application_tags()
        }
        return self.application_info

    # @staticmethod
    # def get_application_info_from_config():
    #     return {
    #         'applicationId': ConfigProvider.get(config_names.ATLAS_APPLICATION_ID),
    #         'applicationInstanceId': ConfigProvider.get(config_names.ATLAS_APPLICATION_INSTANCE_ID),
    #         'applicationDomainName': ConfigProvider.get(config_names.ATLAS_APPLICATION_DOMAIN_NAME, ''),
    #         'applicationClassName': ConfigProvider.get(config_names.ATLAS_APPLICATION_CLASS_NAME, ''),
    #         'applicationName': ConfigProvider.get(config_names.ATLAS_APPLICATION_NAME, ''),
    #         'applicationVersion': ConfigProvider.get(config_names.ATLAS_APPLICATION_VERSION, ''),
    #         'applicationStage': ConfigProvider.get(config_names.ATLAS_APPLICATION_STAGE, ''),
    #         'applicationRegion': ConfigProvider.get(config_names.ATLAS_APPLICATION_REGION, ''),
    #         'applicationRuntime': 'python',
    #         'applicationRuntimeVersion': str(sys.version_info[0]),
    #         'applicationTags': ApplicationInfoProvider.parse_application_tags()
    #     }

    @staticmethod
    def get_default_application_id(app_name):
        return "python:" + app_name

    @staticmethod
    def get_default_application_instance_id(app_name):
        # hostname = socket.gethostname()
        return str(uuid.uuid4())
        # return '{app_name}:{id}@{hostname}'.format(app_name=app_name, id=str(uuid.uuid4()), hostname=hostname)
