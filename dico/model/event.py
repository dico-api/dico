import datetime
from .channel import Channel, Message
from .guild import Guild
from .permission import Role
from .snowflake import Snowflake
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


ChannelCreate = Channel
ChannelUpdate = Channel
ChannelDelete = Channel


class ChannelPinsUpdate(EventBase):
    def __init__(self, client, resp: dict):
        super().__init__(client, resp)
        self.guild_id = Snowflake.optional(resp.get("guild_id"))
        self.channel_id = Snowflake(resp["channel_id"])
        self.__last_pin_timestamp = resp.get("last_pin_timestamp")
        self.last_pin_timestamp = datetime.datetime.fromisoformat(self.__last_pin_timestamp) if self.__last_pin_timestamp else self.__last_pin_timestamp

    @property
    def channel(self):
        return self.client.get_channel(self.channel_id)

    @property
    def guild(self):
        if self.guild_id:
            return self.client.get_guild(self.guild_id)


GuildCreate = Guild
GuildUpdate = Guild
GuildDelete = Guild


class GuildRoleCreate(EventBase):
    def __init__(self, client, resp: dict):
        super().__init__(client, resp)
        self.guild_id = Snowflake(resp["guild_id"])
        self.role = Role(client, resp["role"], guild_id=self.guild_id)

    @property
    def guild(self):
        return self.client.get_guild(self.guild_id)


class GuildRoleUpdate(GuildRoleCreate):
    pass


class GuildRoleDelete(EventBase):
    def __init__(self, client, resp: dict):
        super().__init__(client, resp)
        self.guild_id = Snowflake(resp["guild_id"])
        self.role_id = Snowflake(resp["role_id"])

    @property
    def guild(self):
        return self.client.get_guild(self.guild_id)

    @property
    def role(self):
        return self.guild.get_role(self.role_id)


MessageCreate = Message
MessageUpdate = Message


class MessageDelete(EventBase):
    def __init__(self, client, resp: dict):
        super().__init__(client, resp)
        self.id = Snowflake(resp["id"])
        self.channel_id = Snowflake(resp["channel_id"])
        self.guild_id = Snowflake.optional(resp.get("guild_id"))

    @property
    def channel(self):
        return self.client.get_channel(self.channel_id)

    @property
    def guild(self):
        if self.guild_id:
            return self.client.get_guild(self.guild_id)
