import uuid


class WatcherOptions:
    # Use the specified Username to authenticate the current connection
    username = None
    # Optional password. Must match the password specified in the
    # requirepass server configuration option (if connecting to a Redis 5.0 instance, or lower),
    # or the User Password when connecting to a Redis 6.0 instance, or greater,
    # that is using the Redis ACL system.
    password = None
    # host: port, address.
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
