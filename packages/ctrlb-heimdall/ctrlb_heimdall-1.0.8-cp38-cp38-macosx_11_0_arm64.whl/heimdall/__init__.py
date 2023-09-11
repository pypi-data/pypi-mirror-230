import atexit

from heimdall.probe.dynamicConfig.dynamic_config_manager import DynamicConfigManager

from . import cdbg_native
from .broker.broker_manager import BrokerManager
from .probe.breakpoints.tracepoint import TracePointManager
from .probe.breakpoints.logpoint import LogPointManager
from .probe.error_stack_manager import ErrorStackManager
from heimdall.config.config_provider import ConfigProvider
from heimdall.config import config_names




tracepoint_data_redaction_callback = None
log_data_redaction_callback = None

from heimdall.utils import get_logger
logger = get_logger(__name__)

def initialize_config_provider(apikey, debug, auto_instrumentation, application_name, application_stage, application_version):
    config = {}
    if apikey:
        config["atlas.apikey"] = apikey
    if debug:
        config["atlas.debug.enable"] = str(debug)
    if auto_instrumentation:
        config["atlas.auto.instrumentation.enable"] = str(auto_instrumentation)
    if application_name:
        config["atlas.application.name"] = application_name
    if application_stage:
        config["atlas.application.stage"] = application_stage
    if application_version:
        config["atlas.application.version"] = application_version

    ## Set the application_name from git if not provided
    def get_active_git_repository_name():
        try:
            # Run the git command to get the remote URL of the origin
            import subprocess
            result = subprocess.run(['git', 'remote', 'get-url', 'origin'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)

            # Extract the repository name from the URL
            url = result.stdout.strip()
            if url.endswith('.git'):
                return url.split('/')[-1][:-4]
            else:
                return url.split('/')[-1]

        except subprocess.CalledProcessError as e:
            return None
    repo_name = get_active_git_repository_name()
    ConfigProvider.__init__(repo_name, config)

def start(apikey = None,
          debug = None,
          auto_instrumentation = None,
          application_name = None,
          application_stage = None,
          application_version = None,
          log_data_redaction_callback=None,
          tracepoint_data_redaction_callback=None, 
          ):
    initialize_config_provider(apikey, debug, auto_instrumentation, application_name, application_stage, application_version)
    if ConfigProvider.get(config_names.ATLAS_AUTO_INSTRUMENTATION_ENABLE, False):
        from . import configure_autoinstrumentation
        configure_autoinstrumentation.initialize()
    cdbg_native.InitializeModule(None)
    _broker_manager = BrokerManager().instance()
    TracePointManager(broker_manager=_broker_manager, data_redaction_callback=tracepoint_data_redaction_callback)
    LogPointManager(broker_manager=_broker_manager, data_redaction_callback=log_data_redaction_callback)
    esm = ErrorStackManager(broker_manager=_broker_manager)
    dcm = DynamicConfigManager(broker_manager=_broker_manager)
    _broker_manager.initialize()
    esm.start()
    atexit.register(dcm.handle_detach)
