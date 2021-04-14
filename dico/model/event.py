from .channel import Message


class EventBase:
    def __init__(self, resp: dict):
        pass

    @classmethod
    def create(cls, resp: dict):
        return cls(resp)


class Ready(EventBase):
    # noinspection PyMissingConstructor
    def __init__(self, resp: dict):
        self.v = resp["v"]
        self.user = resp["user"]
        self.private_channels = resp["private_channels"]
        self.guilds = resp["guilds"]
        self.session_id = resp["session_id"]
        self.shard = resp.get("shard", [])
        self.application = resp["application"]


class MessageCreate(EventBase):
    # noinspection PyMissingConstructor
    def __init__(self, resp: dict):
        self.message = Message(resp)
