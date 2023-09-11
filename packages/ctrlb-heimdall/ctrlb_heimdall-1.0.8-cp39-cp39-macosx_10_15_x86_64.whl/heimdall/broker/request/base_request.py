from heimdall.broker.request.request import Request
import multiprocessing


class BaseRequest(Request):

    def __init__(self, id, client=None):
        self.id = id
        self.client = client
        self._pid = multiprocessing.current_process().pid


    def get_id(self):
        return self.id

    def get_name(self):
        return self.__class__.__name__

    def get_client(self):
        return self.client
