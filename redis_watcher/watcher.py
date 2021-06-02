# refer to https://github.com/pycasbin/postgresql-watcher,
# https://github.com/ScienceLogic/pycasbin-redis-watcher/blob/master/casbin_redis_watcher/watcher.py
# and https://github.com/casbin/redis-watcher
import time
from multiprocessing import Process, Pipe
from typing import Optional, Callable
import redis

REDIS_CHANNEL_NAME = "casbin_role_watcher"

def casbin_subscription(
        process_conn: Pipe,
        host: str,
        db:str,
        password: str,
        port: Optional[int] = 6379,
        delay: Optional[int] = 2,
        channel_name: Optional[str] = REDIS_CHANNEL_NAME,
):
    time.sleep(delay)
    conn = redis.Redis(host=host, port=port, password=password,db=db)
    p=conn.pubsub()
    p.subscribe(channel_name)
    print("Waiting for casbin policy update...")
    while True and conn:
        try:
            msg=p.get_message(timeout=30)

        except Exception as e:
            print("Casbin watcher faild to get msg from redis due to{}".format(e))
            p.close()
            conn=None
            break

        if msg:
            if msg.get('type')=='subscribe':
                pass
            if msg.get('type')=='message':
                print("Casbin policy update identified Message was {}".format(msg['data'].decode()))
            try:
                process_conn.send(msg['data'])
            except Exception as e:

                print("Casbin faild send policy updage msg to piped process due to {}".format(e))
                p.close()
                conn=None
                break



class RedisWatcher(object):
    def __init__(
            self,
            host: str,
            db: str,
            password: str,
            port: Optional[int] = 6379,
            channel_name: Optional[str] = REDIS_CHANNEL_NAME,
            start_process: Optional[bool] = True,
    ):
        self.update_callback = self.default_update_callback
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.channel_name = channel_name
        self.subscribed_process,self.parent_conn = self.create_subscriber_process(start_process)

    def create_subscriber_process(
            self,
            start_process: Optional[bool] = True,
            delay: Optional[int] = 2,
    ):
        parent_conn, child_conn = Pipe()
        self.parent_conn=parent_conn
        p = Process(
            target=casbin_subscription,
            args=(
                child_conn,
                self.host,
                self.db,
                self.password,
                self.port,
                delay,
                self.channel_name,
            ),

            daemon=True,
        )
        if start_process:
            p.start()
        self.should_reload()
        return child_conn,parent_conn

    def set_update_callback(self, fn_name):
        print("runtime is set update callback", fn_name)
        self.update_callback = fn_name

    def default_update_callback(self):
        print("this func is called,because policy is changed!")

    def update(self):
        conn = redis.Redis(
            host=self.host,
            port=self.port,
            db=self.db,
            password=self.password,
        )
        conn.publish(self.channel_name,f'casbin policy update at {time.time()}')
        self.update_callback()
        return True

    def should_reload(self):
        try:
            if self.parent_conn:
                message = self.parent_conn.recv()
                print(f"message:{message}")
                return True
        except EOFError:
            print(
                "Child casbin-watcher subscribe process has stopped, "
                "attempting to recreate the process in 10 seconds..."
            )
            (self.subscribed_process, self.parent_conn) = self.create_subscriber_process(
                delay=10
            )
            return False
