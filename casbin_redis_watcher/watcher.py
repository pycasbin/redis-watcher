from redis import Redis
from options import WatcherOptions
from casbin.persist.watcher import Watcher as Casbin_Watcher
import json


class Watcher:

    def __init__(self):
        self.l = None
        self.sub_client: Redis.client = None
        self.pub_client: Redis.client = None
        self.options: WatcherOptions = None
        self.close = None
        self.callback: callable = None
        self.ctx = None


class MSG:

    def __init__(self):
        self.method: str = ""
        self.ID: str = ""
        self.sec: str = ""
        self.ptype: str = ""
        self.params = None

    def marshal_binary(self):
        return json.dumps(self.__dict__)

    def unmarshal_binary(self, data: bytes):
        return json.loads(data, )


def new_watcher(addr: str, option: WatcherOptions) -> Casbin_Watcher:
    option.addr = addr



m = MSG()
m.method = "xxx"
print(m.marshal_binary())
