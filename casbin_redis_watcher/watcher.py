from redis import Redis
from options import WatcherOptions
from casbin.persist.watcher import Watcher as Casbin_Watcher
import json


class WatcherError(Exception):
    pass


class Watcher:

    def __init__(self):
        self.mutex = None
        self.sub_client: Redis.client = None
        self.pub_client: Redis.client = None
        self.options: WatcherOptions = None
        self.close = None
        self.callback: callable = None
        self.ctx = None

    def init_config(self, option: WatcherOptions):
        if option.optional_update_callback is not None:
            self.set_update_callback(option.optional_update_callback)
        else:
            raise WatcherError("Casbin Redis Watcher callback not set when an update was received")

    def set_update_callback(self, option: WatcherOptions):
        pass


class MSG:

    def __init__(self, method="", ID="", sec="", ptype="", params=None):
        self.method: str = method
        self.ID: str = ID
        self.sec: str = sec
        self.ptype: str = ptype
        self.params = params

    def marshal_binary(self):
        return json.dumps(self.__dict__)

    @staticmethod
    def unmarshal_binary(data: bytes):
        loaded = json.loads(data)
        return MSG(**loaded)


def new_watcher(addr: str, option: WatcherOptions) -> Casbin_Watcher:
    option.addr = addr
    option.init_config()

    w = Watcher()
    w.sub_client = Redis().client()
    w.pub_client = Redis().client()
    w.ctx = None
    w.close = None


m = MSG()
m.method = "xxx"
encoded = m.marshal_binary().encode()
decoded = m.unmarshal_binary(encoded)
print(decoded)
