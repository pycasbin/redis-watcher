# redis-watcher

[![GitHub Action](https://github.com/pycasbin/redis-watcher/workflows/build/badge.svg?branch=master)](https://github.com/pycasbin/redis-watcher/actions)
[![Coverage Status](https://coveralls.io/repos/github/pycasbin/redis-watcher/badge.svg)](https://coveralls.io/github/pycasbin/redis-watcher)
[![Version](https://img.shields.io/pypi/v/casbin-redis-watcher.svg)](https://pypi.org/project/casbin-redis-watcher/)
[![PyPI - Wheel](https://img.shields.io/pypi/wheel/casbin-redis-watcher.svg)](https://pypi.org/project/casbin-redis-watcher/)
[![Pyversions](https://img.shields.io/pypi/pyversions/casbin-redis-watcher.svg)](https://pypi.org/project/casbin-redis-watcher/)
[![Download](https://img.shields.io/pypi/dm/casbin-redis-watcher.svg)](https://pypi.org/project/casbin-redis-watcher/)
[![Discord](https://img.shields.io/discord/1022748306096537660?logo=discord&label=discord&color=5865F2)](https://discord.gg/S5UjpzGZjN)

redis-watcher is the [Redis](https://github.com/redis/redis) watcher for [pycasbin](https://github.com/casbin/pycasbin). With this library, Casbin can synchronize the policy with the database in multiple enforcer instances.

## Installation

    pip install casbin-redis-watcher

## Simple Example

```python
import os
import casbin
from casbin_redis_watcher import new_watcher, WatcherOptions

def callback_function(event):
    print("update for remove filtered policy callback, event: {}".format(event))

def get_examples(path):
    examples_path = os.path.split(os.path.realpath(__file__))[0] + "/../examples/"
    return os.path.abspath(examples_path + path)

if __name__ == "main":
    test_option = WatcherOptions()
    test_option.host = "localhost"
    test_option.port = "6379"
    test_option.channel = "test"
    test_option.ssl = False
    test_option.optional_update_callback = callback_function
    w = new_watcher(test_option)
    
    e = casbin.Enforcer(
        get_examples("rbac_model.conf"), get_examples("rbac_policy.csv")
    )
    e.set_watcher(w)
    # then the callback function will be called when the policy is updated.
    e.save_policy()
   
```

## Getting Help

- [pycasbin](https://github.com/casbin/pycasbin)

## License

This project is under Apache 2.0 License. See the [LICENSE](LICENSE) file for the full license text.

