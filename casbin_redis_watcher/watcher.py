from redis.client import Redis
from options import WatcherOptions
from casbin.persist.watcher import Watcher as Casbin_Watcher

import asyncio
import json


class WatcherError(Exception):
    pass


class Watcher:

    def __init__(self):
        self.mutex: asyncio.Lock = asyncio.Lock()
        self.sub_client: Redis = None
        self.pub_client: Redis = None
        self.options: WatcherOptions = None
        self.close = None
        self.callback: callable = None
        self.ctx = None

    def init_config(self, option: WatcherOptions):
        if option.optional_update_callback:
            self.set_update_callback(option.optional_update_callback)
        else:
            raise WatcherError("Casbin Redis Watcher callback not "
                               "set when an update was received")
        if option.sub_client:
            self.sub_client = option.sub_client
        else:
            self.sub_client = Redis().client()

    async def set_update_callback(self, callback: callable):
        async with self.mutex:
            self.callback = callback

    def update(self):

        async def func():
            async with self.mutex:
                return self.pub_client.publish()

        return self.log_record(func)


    def log_record(self, f: callable):
        err = f()
        if err:
            print(err)
        return err


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
