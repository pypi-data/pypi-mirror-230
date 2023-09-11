from heimdall.probe.coded_exception import CodedException
from heimdall.probe.errors import TRACEPOINT_ALREADY_EXIST
from heimdall.probe.breakpoints.tracepoint import TracePointManager
from heimdall.broker.handler.response.response_handler import ResponseHandler
from heimdall.probe.response.tracePoint.filter_tracepoints_response import FilterTracePointsResponse

from heimdall.utils.validation import validate_file_name_and_line_no

from heimdall.utils import get_logger
logger = get_logger(__name__)

def _applyTracePoint(trace_point):
    try:
        validate_file_name_and_line_no(trace_point.get("fileName"), trace_point.get("lineNo"))
        condition = trace_point.get("condition", None)
        client = trace_point.get("client", None)
        file_name = trace_point.get("fileName", None)
        trace_point_manager = TracePointManager.instance()
        tags = trace_point.get("tags", set())
        if tags == None:
            tags = set()
        trace_point_manager.put_trace_point(trace_point.get("id", None), file_name, 
                                            trace_point.get("fileHash", None), trace_point.get("lineNo",None),
                                            client, trace_point.get("expireSecs", None), trace_point.get("expireCount", None),
                                            trace_point.get("tracingEnabled", None), condition = condition,
                                            tags=tags)
        
        trace_point_manager.publish_application_status()
        if client is not None:
            trace_point_manager.publish_application_status(client)

    except Exception as e:
        skip_logging = False
        if isinstance(e, CodedException):
            if e.code == TRACEPOINT_ALREADY_EXIST.code:
                skip_logging = True
                trace_point_manager.publish_application_status()
                if client is not None:
                    trace_point_manager.publish_application_status(client)
        if not skip_logging:
            logger.error("Unable to apply tracepoint %s" % e)

class FilterTracePointsResponseHandler(ResponseHandler):
    RESPONSE_NAME = "FilterTracePointsResponse"


    @staticmethod
    def get_response_name():
        return FilterTracePointsResponseHandler.RESPONSE_NAME

    
    @staticmethod
    def get_response_cls():
        return FilterTracePointsResponse


    @staticmethod
    def handle_response(response):
        trace_points = response.trace_points
        for trace_point in trace_points:
            _applyTracePoint(trace_point)
    