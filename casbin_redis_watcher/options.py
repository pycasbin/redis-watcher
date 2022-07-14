import redis
import uuid


class WatcherOptions:

    addr = None
    sub_client = None
    pub_client = None
    channel = None
    ignore_self = None
    local_ID = None
    optional_update_callback = None

    def init_config(self):

        if self.local_ID == "":
            self.local_ID = uuid.uuid4()

        if self.channel == "":
            self.channel = "/casbin"
