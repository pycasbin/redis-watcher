import uuid


class WatcherOptions:
    password = None
    host = "localhost"
    port = "6379"
    sub_client = None
    pub_client = None
    channel = None
    ignore_self = None
    local_ID = None
    optional_update_callback = None

    def init_config(self):

        if self.local_ID is None:
            self.local_ID = str(uuid.uuid4())

        if self.channel is None:
            self.channel = "/casbin"
