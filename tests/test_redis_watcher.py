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

import os
import time
from unittest import TestCase

import casbin
import redis

from casbin_redis_watcher import new_watcher, WatcherOptions


def get_examples(path):
    examples_path = os.path.split(os.path.realpath(__file__))[0] + "/../examples/"
    return os.path.abspath(examples_path + path)


class TestConfig(TestCase):
    def test_watcher_init(self):
        test_option = WatcherOptions()
        test_option.host = "localhost"
        test_option.port = "6379"
        test_option.optional_update_callback = lambda event: print("update callback, event: {}".format(event))
        w = new_watcher(test_option)
        assert isinstance(w.sub_client, redis.client.PubSub)
        assert isinstance(w.pub_client, redis.client.Redis)

    def test_watcher_init_without_callback(self):
        test_option = WatcherOptions()
        test_option.host = "localhost"
        test_option.port = "6379"
        w = new_watcher(test_option)
        assert isinstance(w.sub_client, redis.client.PubSub)
        assert isinstance(w.pub_client, redis.client.Redis)

    def test_unsubscribe(self):
        callback_flag = False

        def callback_function(event):
            nonlocal callback_flag
            callback_flag = True
            print("callback_function, event: {}".format(event))

        test_option = WatcherOptions()
        test_option.host = "localhost"
        test_option.port = "6379"
        test_option.channel = "test"
        test_option.optional_update_callback = callback_function
        w = new_watcher(test_option)
        assert callback_flag is False
        w.pub_client.publish("test", "test_value")
        time.sleep(0.5)
        assert callback_flag is True
        w.unsubscribe(w.sub_client)
        time.sleep(0.5)
        callback_flag = False
        w.pub_client.publish("test", "test_value")
        time.sleep(0.5)
        assert callback_flag is False

    def test_call_back_function(self):
        callback_flag = False

        def callback_function(event):
            nonlocal callback_flag
            callback_flag = True
            print("callback_function, event: {}".format(event))

        test_option = WatcherOptions()
        test_option.host = "localhost"
        test_option.port = "6379"
        test_option.channel = "test"
        test_option.optional_update_callback = callback_function
        w = new_watcher(test_option)
        assert callback_flag is False
        w.pub_client.publish("test", "test_value")
        time.sleep(0.5)
        assert callback_flag is True

    def test_update(self):
        callback_flag = False

        def callback_function(event):
            nonlocal callback_flag
            callback_flag = True
            print("update callback, event: {}".format(event))

        test_option = WatcherOptions()
        test_option.host = "localhost"
        test_option.port = "6379"
        test_option.channel = "test"
        test_option.optional_update_callback = callback_function
        w = new_watcher(test_option)
        assert callback_flag is False
        w.update()
        time.sleep(0.5)
        assert callback_flag is True

    def test_update_for_add_policy(self):
        callback_flag = False

        def callback_function(event):
            nonlocal callback_flag
            callback_flag = True
            print("update for add policy, event: {}".format(event))

        test_option = WatcherOptions()
        test_option.host = "localhost"
        test_option.port = "6379"
        test_option.channel = "test"
        test_option.optional_update_callback = callback_function
        w = new_watcher(test_option)
        assert callback_flag is False
        w.update_for_add_policy("test1", "test2", "test3")
        time.sleep(0.5)
        assert callback_flag is True

    def test_update_for_remove_policy(self):
        callback_flag = False

        def callback_function(event):
            nonlocal callback_flag
            callback_flag = True
            print("update for remove policy callback, event: {}".format(event))

        test_option = WatcherOptions()
        test_option.host = "localhost"
        test_option.port = "6379"
        test_option.channel = "test"
        test_option.optional_update_callback = callback_function
        w = new_watcher(test_option)
        assert callback_flag is False
        w.update_for_remove_policy("test1", "test2", "test3")
        time.sleep(0.5)
        assert callback_flag is True

    def test_update_for_remove_filtered_policy(self):
        callback_flag = False

        def callback_function(event):
            nonlocal callback_flag
            callback_flag = True
            print("update for remove filtered policy callback, event: {}".format(event))

        test_option = WatcherOptions()
        test_option.host = "localhost"
        test_option.port = "6379"
        test_option.channel = "test"
        test_option.optional_update_callback = callback_function
        w = new_watcher(test_option)
        assert callback_flag is False
        w.update_for_remove_filtered_policy("test1", "test2", "test3")
        time.sleep(0.5)
        assert callback_flag is True

    def test_with_enforcer(self):
        callback_flag = False

        def callback_function(event):
            nonlocal callback_flag
            callback_flag = True
            print("update for remove filtered policy callback, event: {}".format(event))

        test_option = WatcherOptions()
        test_option.host = "localhost"
        test_option.port = "6379"
        test_option.channel = "test"
        test_option.optional_update_callback = callback_function
        w = new_watcher(test_option)

        e = casbin.Enforcer(get_examples("rbac_model.conf"), get_examples("rbac_policy.csv"))
        e.set_watcher(w)
        assert callback_flag is False
        e.save_policy()
        time.sleep(0.5)
        assert callback_flag is True

        # related update function not be called in py-casbin yet
        e.add_policy("eve", "data3", "read")
        e.remove_policy("eve", "data3", "read")
        rules = [
            ["jack", "data4", "read"],
            ["katy", "data4", "write"],
            ["leyo", "data4", "read"],
            ["ham", "data4", "write"],
        ]
        e.add_policies(rules)
        e.remove_policies(rules)
