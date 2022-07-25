# Copyright 2022 The casbin Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import logging
from threading import Thread, Lock, Event

from casbin.model import Model
from redis.client import Redis, PubSub

from casbin_redis_watcher.options import WatcherOptions


class RedisWatcher:
    def __init__(self):
        self.mutex: Lock = Lock()
        self.sub_client: PubSub = None
        self.pub_client: Redis = None
        self.options: WatcherOptions = None
        self.close = None
        self.callback: callable = None
        self.ctx = None
        self.subscribe_thread: Thread = Thread(target=self.subscribe, daemon=True)
        self.subscribe_event = Event()
        self.logger = logging.getLogger(__name__)

    def init_config(self, option: WatcherOptions):
        if option.optional_update_callback:
            self.set_update_callback(option.optional_update_callback)
        else:
            self.logger.warning("No callback function is set.Use the default callback function.")
            self.callback = self.default_callback_func

        rds = Redis(host=option.host, port=option.port, password=option.password)

        if option.sub_client:
            self.sub_client = option.sub_client
        else:
            self.sub_client = rds.client().pubsub()

        if option.pub_client:
            self.pub_client = option.pub_client
        else:
            self.pub_client = rds.client()

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
                return self.pub_client.publish(self.options.channel, msg.marshal_binary())

        return self.log_record(func)

    def update_for_remove_policy(self, sec: str, ptype: str, *params: str):
        def func():
            with self.mutex:
                msg = MSG("UpdateForRemovePolicy", self.options.local_ID, sec, ptype, params)
                return self.pub_client.publish(self.options.channel, msg.marshal_binary())

        return self.log_record(func)

    def update_for_remove_filtered_policy(self, sec: str, ptype: str, field_index: int, *params: str):
        def func():
            with self.mutex:
                msg = MSG(
                    "UpdateForRemoveFilteredPolicy",
                    self.options.local_ID,
                    sec,
                    ptype,
                    f"{field_index} {' '.join(params)}",
                )
                return self.pub_client.publish(self.options.channel, msg.marshal_binary())

        return self.log_record(func)

    def update_for_save_policy(self, model: Model):
        def func():
            with self.mutex:
                msg = MSG(
                    "UpdateForSavePolicy",
                    self.options.local_ID,
                    "",
                    "",
                    model.to_text(),
                )
                return self.pub_client.publish(self.options.channel, msg.marshal_binary())

        return self.log_record(func)

    @staticmethod
    def default_callback_func(msg: str):
        print("callback: " + msg)

    @staticmethod
    def log_record(f: callable):
        try:
            result = f()
        except Exception as e:
            print(f"Casbin Redis Watcher error: {e}")
        else:
            return result

    @staticmethod
    def unsubscribe(psc: PubSub):
        return psc.unsubscribe()

    def subscribe(self):
        self.sub_client.subscribe(self.options.channel)
        for item in self.sub_client.listen():
            if not self.subscribe_event.is_set():
                self.subscribe_event.set()
            if item is not None and item["type"] == "message":
                with self.mutex:
                    self.callback(str(item))


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


def new_watcher(option: WatcherOptions):
    option.init_config()
    w = RedisWatcher()
    rds = Redis(host=option.host, port=option.port, password=option.password)
    w.sub_client = rds.client().pubsub()
    w.pub_client = rds.client()
    if w.sub_client.ping() is False or w.pub_client.ping() is False:
        w.logger.error("Casbin Redis Watcher error: Redis connection failed.")
    w.ctx = None
    w.close = None
    w.init_config(option)
    w.close = False
    w.subscribe_thread.start()
    w.subscribe_event.wait(timeout=5)
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
