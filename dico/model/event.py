import datetime
from .channel import *


class EventBase:
    def __init__(self, resp: dict):
        self.raw = resp

    @classmethod
    def create(cls, resp: dict):
        return cls(resp)


class Ready(EventBase):
    def __init__(self, resp: dict):
        super().__init__(resp)
        self.v = resp["v"]
        self.user = resp["user"]
        self.private_channels = resp["private_channels"]
        self.guilds = resp["guilds"]
        self.session_id = resp["session_id"]
        self.shard = resp.get("shard", [])
        self.application = resp["application"]


class ApplicationCommandCreate(EventBase):
    def __init__(self, resp: dict):
        super().__init__(resp)


class ApplicationCommandUpdate(EventBase):
    def __init__(self, resp: dict):
        super().__init__(resp)


class ApplicationCommandDelete(EventBase):
    def __init__(self, resp: dict):
        super().__init__(resp)


class ChannelCreate(EventBase, Channel):
    def __init__(self, resp: dict):
        Channel.__init__(self, resp)
        EventBase.__init__(self, resp)


class ChannelUpdate(EventBase, Channel):
    def __init__(self, resp: dict):
        Channel.__init__(self, resp)
        EventBase.__init__(self, resp)


class ChannelDelete(EventBase, Channel):
    def __init__(self, resp: dict):
        Channel.__init__(self, resp)
        EventBase.__init__(self, resp)


class ChannelPinsUpdate(EventBase):
    def __init__(self, resp: dict):
        super().__init__(resp)
        self.guild_id = resp.get("guild_id")
        self.channel_id = resp["channel_id"]
        self.__last_pin_timestamp = resp.get("last_pin_timestamp")
        self.last_pin_timestamp = datetime.datetime.fromisoformat(self.__last_pin_timestamp) if self.__last_pin_timestamp else self.__last_pin_timestamp


class MessageCreate(EventBase, Message):
    def __init__(self, resp: dict):
        Message.__init__(self, resp)
        EventBase.__init__(self, resp)
