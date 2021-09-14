from redis.client import Redis, PubSub
from options import WatcherOptions
from casbin.persist.watcher import Watcher as Casbin_Watcher
from casbin.model import Model

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
        # TODO
        self.close = None
        self.callback: callable = None
        # TODO
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
            # TODO
            self.sub_client = Redis().client()

        if option.pub_client:
            self.pub_client = option.pub_client
        else:
            # TODO
            self.pub_client = Redis().client()

    async def set_update_callback(self, callback: callable):
        async with self.mutex:
            self.callback = callback

    def update(self):

        async def func():
            async with self.mutex:
                msg = MSG("Update", self.options.local_ID, "", "", "")
                return self.pub_client.publish(self.options.channel, msg)

        return self.log_record(func)

    def update_for_add_policy(self, sec: str, ptype: str, *params: str):

        async def func():
            async with self.mutex:
                msg = MSG("UpdateForAddPolicy", self.options.local_ID, sec, ptype, params)
                return self.pub_client.publish(self.options.channel, msg)

        return self.log_record(func)

    def update_for_remove_policy(self, sec: str, ptype: str, *params: str):

        async def func():
            async with self.mutex:
                msg = MSG("UpdateForRemovePolicy", self.options.local_ID, sec, ptype, params)
                return self.pub_client.publish(self.options.channel, msg)

        return self.log_record(func)

    def update_for_remove_filtered_policy(self, sec: str, ptype: str, field_index: int, *params: str):

        async def func():
            async with self.mutex:
                msg = MSG("UpdateForRemoveFilteredPolicy",
                          self.options.local_ID,
                          sec, ptype, f"{field_index} {' '.join(params)}")
                return self.pub_client.publish(self.options.channel, msg)

        return self.log_record(func)

    def update_for_save_policy(self, model: Model):

        async def func():
            async with self.mutex:
                msg = MSG("UpdateForSavePolicy", self.options.local_ID, "", "", model)
                return self.pub_client.publish(self.options.channel, msg)

        return self.log_record(func)

    @staticmethod
    def log_record(f: callable):
        try:
            result = f()
        except Exception as e:
            print(e)
        else:
            return result

    def unsubscribe(self, psc: PubSub):
        return psc.unsubscribe(self.ctx)


class MSG:

    def __init__(self, method="", ID="", sec="", ptype="", *params):
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


# TODO
def new_watcher(addr: str, option: WatcherOptions) -> Casbin_Watcher:
    option.addr = addr
    option.init_config()

    w = Watcher()
    w.sub_client = Redis().client()
    w.pub_client = Redis().client()
    w.ctx = None
    w.close = None


# TODO
def new_publish_watcher(addr: str, option: WatcherOptions) -> Casbin_Watcher:
    pass


m = MSG()
m.method = "xxx"
encoded = m.marshal_binary().encode()
decoded = m.unmarshal_binary(encoded)
print(decoded)
