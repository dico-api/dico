import datetime
from .channel import *
from ..base.model import EventBase


class Ready(EventBase):
    def __init__(self, client, resp: dict):
        super().__init__(client, resp)
        self.v = resp["v"]
        self.user = resp["user"]
        self.private_channels = resp["private_channels"]
        self.guilds = resp["guilds"]
        self.session_id = resp["session_id"]
        self.shard = resp.get("shard", [])
        self.application = resp["application"]


class ApplicationCommandCreate(EventBase):
    def __init__(self, client, resp: dict):
        super().__init__(client, resp)


class ApplicationCommandUpdate(EventBase):
    def __init__(self, client, resp: dict):
        super().__init__(client, resp)


class ApplicationCommandDelete(EventBase):
    def __init__(self, client, resp: dict):
        super().__init__(client, resp)


class ChannelCreate(EventBase, Channel):
    def __init__(self, client, resp: dict):
        Channel.__init__(self, client, resp)
        EventBase.__init__(self, client, resp)


class ChannelUpdate(EventBase, Channel):
    def __init__(self, client, resp: dict):
        Channel.__init__(self, client, resp)
        EventBase.__init__(self, client, resp)


class ChannelDelete(EventBase, Channel):
    def __init__(self, client, resp: dict):
        Channel.__init__(self, client, resp)
        EventBase.__init__(self, client, resp)


class ChannelPinsUpdate(EventBase):
    def __init__(self, client, resp: dict):
        super().__init__(client, resp)
        self.guild_id = resp.get("guild_id")
        self.channel_id = resp["channel_id"]
        self.__last_pin_timestamp = resp.get("last_pin_timestamp")
        self.last_pin_timestamp = datetime.datetime.fromisoformat(self.__last_pin_timestamp) if self.__last_pin_timestamp else self.__last_pin_timestamp


class MessageCreate(EventBase, Message):
    def __init__(self, client, resp: dict):
        Message.__init__(self, client, resp)
        EventBase.__init__(self, client, resp)
