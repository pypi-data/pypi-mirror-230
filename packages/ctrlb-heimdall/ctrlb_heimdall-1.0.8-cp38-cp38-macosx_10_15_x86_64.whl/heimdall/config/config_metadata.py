from heimdall.config import config_names
from heimdall.config import constants
import uuid

CONFIG_METADATA = {
    config_names.ATLAS_APIKEY: {
        constants.TYPE_STRING: constants.STRING_STRING,
    },
    config_names.ATLAS_DEBUG_ENABLE: {
        constants.TYPE_STRING: constants.BOOLEAN_STRING,
        constants.DEFAULT_VALUE_STRING: False,
    },
    config_names.ATLAS_AUTO_INSTRUMENTATION_ENABLE: {
        constants.TYPE_STRING: constants.BOOLEAN_STRING,
        constants.DEFAULT_VALUE_STRING: False,
    },
    config_names.ATLAS_ERROR_STACK_ENABLE: {
        constants.TYPE_STRING: constants.BOOLEAN_STRING,
        constants.DEFAULT_VALUE_STRING: False,
    },
    config_names.ATLAS_ERROR_COLLECTION_ENABLE_CAPTURE_FRAME: {
        constants.TYPE_STRING: constants.BOOLEAN_STRING,
        constants.DEFAULT_VALUE_STRING: False,
    },
    config_names.ATLAS_PRINT_CLOSED_SOCKET_DATA: {
        constants.TYPE_STRING: constants.BOOLEAN_STRING,
        constants.DEFAULT_VALUE_STRING: False,
    },
    config_names.ATLAS_APPLICATION_ID: {
        constants.TYPE_STRING: constants.STRING_STRING,
    },
    # config_names.ATLAS_APPLICATION_INSTANCE_ID: {
    #     constants.TYPE_STRING: constants.STRING_STRING,
    # },
    config_names.ATLAS_APPLICATION_NAME: {
        constants.TYPE_STRING: constants.STRING_STRING,
        constants.DEFAULT_VALUE_STRING: str(uuid.uuid4()),
    },
    config_names.ATLAS_APPLICATION_STAGE: {
        constants.TYPE_STRING: constants.STRING_STRING,
        constants.DEFAULT_VALUE_STRING: "PROD",
    },
    config_names.ATLAS_APPLICATION_DOMAIN_NAME: {
        constants.TYPE_STRING: constants.STRING_STRING,
        constants.DEFAULT_VALUE_STRING: constants.API_STRING,
    },
    config_names.ATLAS_APPLICATION_CLASS_NAME: {
        constants.TYPE_STRING: constants.STRING_STRING,
        constants.DEFAULT_VALUE_STRING: constants.AWS_STRING,
    },
    config_names.ATLAS_APPLICATION_VERSION: {
        constants.TYPE_STRING: constants.STRING_STRING,
        constants.DEFAULT_VALUE_STRING: "1.0.0",
    },
    config_names.ATLAS_APPLICATION_TAG_PREFIX: {
        constants.TYPE_STRING: constants.ANY_STRING,
    },
}
