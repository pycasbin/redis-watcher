import pytest
redis_published_message = ""
import redis

@pytest.fixture
def fake_redis(monkeypatch):
    from fakeredis import FakeStrictRedis as Redis

    # publish isn't implemented in FakeRedis:(
    def fake_publish(message):
        redis_published_message = message

    # pubsub.subcsribe isn't timplemented in Fake Redis :(
    class fake_socket():
        def getaddrinfo(host, port, family, type, proto, flags):
            pass

    class fake_pubsub():
        _socket = fake_socket()
        def subscribe(self, channel):
            pass
        def getaddrinfo(self):
            pass
        def execute_command(self):
            pass

    monkeypatch.setattr(Redis, 'publish', fake_publish)
    monkeypatch.setattr(Redis, 'pubsub', fake_pubsub)
    return Redis

@pytest.fixture
def fake_redis_server():
    from fakeredis import FakeServer
    server = FakeServer()
    return server

@pytest.fixture
def redis_watcher(fake_redis, fake_redis_server):
    from watcher import RedisWatcher
    rw = RedisWatcher(host='localhost', db=0,password="")
    return rw



def test_update(redis_watcher, fake_redis):

    import watcher
    Redis = fake_redis
    watcher.Redis = fake_redis
    redis_watcher.update()
    assert redis_watcher.should_reload()
    pass

def test_no_reload(redis_watcher):
    assert not redis_watcher.should_reload()

def test_default_update_callback(redis_watcher):
    assert redis_watcher.update_callback() is None

def test_set_update_callback(redis_watcher):
    def tst_callback():
        pass
    redis_watcher.set_update_callback(tst_callback)
    assert redis_watcher.update_callback == tst_callback
