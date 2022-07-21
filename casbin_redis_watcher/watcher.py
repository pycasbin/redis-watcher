import json
from threading import Thread, Lock

from casbin.model import Model
from redis.client import Redis, PubSub

from casbin_redis_watcher.options import WatcherOptions


class WatcherError(Exception):
    pass


class RedisWatcher:

    def __init__(self):
        self.mutex: Lock = Lock()
        self.sub_client: Redis = None
        self.pub_client: Redis = None
        self.options: WatcherOptions = None
        # TODO
        self.close = None
        self.callback: callable = None
        # TODO
        self.ctx = None
        self.subscribe_thread: Thread = Thread(target=self.subscribe, daemon=True)

    def init_config(self, option: WatcherOptions):
        if option.optional_update_callback:
            self.set_update_callback(option.optional_update_callback)
        else:
            raise WatcherError("Casbin Redis Watcher callback not "
                               "set when an update was received")
        if option.sub_client:
            self.sub_client = option.sub_client
        else:
            self.sub_client = Redis(host=option.host, port=option.port).client()

        if option.pub_client:
            self.pub_client = option.pub_client
        else:
            self.pub_client = Redis(host=option.host, port=option.port).client()

        self.options = option

    def set_update_callback(self, callback: callable):
        with self.mutex:
            self.callback = callback

    def update(self):

        def func():
            with self.mutex:
                msg = MSG("Update", self.options.local_ID, "", "", "")
                return self.pub_client.publish(self.options.channel, msg.marshal_binary())

        return self.log_record(func)

    def update_for_add_policy(self, sec: str, ptype: str, *params: str):

        def func():
            with self.mutex:
                msg = MSG("UpdateForAddPolicy", self.options.local_ID, sec, ptype, params)
                return self.pub_client.publish(self.options.channel, msg)

        return self.log_record(func)

    def update_for_remove_policy(self, sec: str, ptype: str, *params: str):

        def func():
            with self.mutex:
                msg = MSG("UpdateForRemovePolicy", self.options.local_ID, sec, ptype, params)
                return self.pub_client.publish(self.options.channel, msg)

        return self.log_record(func)

    def update_for_remove_filtered_policy(self, sec: str, ptype: str, field_index: int, *params: str):

        def func():
            with self.mutex:
                msg = MSG("UpdateForRemoveFilteredPolicy",
                          self.options.local_ID,
                          sec, ptype, f"{field_index} {' '.join(params)}")
                return self.pub_client.publish(self.options.channel, msg)

        return self.log_record(func)

    def update_for_save_policy(self, model: Model):

        def func():
            with self.mutex:
                msg = MSG("UpdateForSavePolicy", self.options.local_ID, "", "", model)
                return self.pub_client.publish(self.options.channel, msg)

        return self.log_record(func)

    @staticmethod
    def log_record(f: callable):
        try:
            result = f()
        except Exception as e:
            print(f"Casbin Redis Watcher error: {e}")
        else:
            return result

    def unsubscribe(self, psc: PubSub):
        return psc.unsubscribe(self.ctx)

    def subscribe(self):
        r = self.sub_client.pubsub()
        r.subscribe(self.options.channel)
        while True:
            ret = r.get_message()
            if ret is not None:
                with self.mutex:
                    self.callback(ret)


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
def new_watcher(option: WatcherOptions):
    option.init_config()
    w = RedisWatcher()
    w.sub_client = Redis(host=option.host, port=option.port).client()
    w.pub_client = Redis(host=option.host, port=option.port).client()
    w.ctx = None
    w.close = None
    w.init_config(option)
    w.close = False
    w.subscribe_thread.start()
    return w


# TODO
def new_publish_watcher(addr: str, option: WatcherOptions):
    option.addr = addr
    w = RedisWatcher()
    w.pub_client = Redis().client()
    w.ctx = None
    w.close = None
    w.init_config(option)
    return w

# m = MSG()
# m.method = "xxx"
# encoded = m.marshal_binary().encode()
# decoded = m.unmarshal_binary(encoded)
# print(decoded)
