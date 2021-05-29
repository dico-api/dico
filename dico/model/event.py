import datetime
from .channel import Channel, Message
from .emoji import Emoji
from .gateway import Activity
from .guild import Guild, Member
from .permission import Role
from .snowflake import Snowflake
from .user import User
from .voice import VoiceState
from .interactions import Interaction
from ..base.model import EventBase


class Ready(EventBase):
    def __init__(self, client, resp: dict):
        super().__init__(client, resp)
        self.v = resp["v"]
        self.user = User.create(client, resp["user"])
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


class ChannelUpdate(Channel):
    def __del__(self):
        Channel.create(self.client, self.raw)

    @classmethod
    def create(cls, client, resp, **kwargs):
        return cls(client, resp, **kwargs)

    @property
    def original(self):
        if self.client.has_cache:
            return self.client.get_channel(self.id)


class ChannelDelete(Channel):
    def __del__(self):
        if self.client.has_cache:
            self.client.cache.remove(self.id, self._cache_type)


class ChannelPinsUpdate(EventBase):
    def __init__(self, client, resp: dict):
        super().__init__(client, resp)
        self.guild_id = Snowflake.optional(resp.get("guild_id"))
        self.channel_id = Snowflake(resp["channel_id"])
        self.__last_pin_timestamp = resp.get("last_pin_timestamp")
        self.last_pin_timestamp = datetime.datetime.fromisoformat(self.__last_pin_timestamp) if self.__last_pin_timestamp else self.__last_pin_timestamp

    @property
    def channel(self):
        if self.client.has_cache:
            return self.client.get(self.channel_id, "channel")

    @property
    def guild(self):
        if self.guild_id:
            return self.client.get(self.guild_id, "guild")


GuildCreate = Guild
GuildUpdate = Guild
GuildDelete = Guild


class GuildBanAdd(EventBase):
    def __init__(self, client, resp: dict):
        super().__init__(client, resp)
        self.guild_id = Snowflake(resp["guild_id"])
        self.user = User.create(self.client, resp["user"])

    @property
    def guild(self):
        if self.client.has_cache:
            return self.client.get(self.guild_id, "guild")


class GuildBanRemove(GuildBanAdd):
    pass


class GuildEmojisUpdate(EventBase):
    def __init__(self, client, resp: dict):
        super().__init__(client, resp)
        self.guild_id = Snowflake(resp["guild_id"])
        self.emojis = [Emoji(self.client, x) for x in resp["emojis"]]

    @property
    def guild(self):
        if self.client.has_cache:
            return self.client.get(self.guild_id, "guild")


class GuildIntegrationsUpdate(EventBase):
    def __init__(self, client, resp: dict):
        super().__init__(client, resp)
        self.guild_id = Snowflake(resp["guild_id"])

    @property
    def guild(self):
        if self.client.has_cache:
            return self.client.get(self.guild_id, "guild")


GuildMemberAdd = Member


class GuildMemberRemove(EventBase):
    def __init__(self, client, resp: dict):
        super().__init__(client, resp)
        self.guild_id = Snowflake(resp["guild_id"])
        self.user = User.create(self.client, resp["user"])

    def __del__(self):
        if self.client.has_cache:
            self.guild.cache.remove(self.user.id, "member")

    @property
    def guild(self):
        if self.client.has_cache:
            return self.client.get(self.guild_id, "guild")

    @property
    def member(self):
        if self.client.has_cache:
            return self.guild.get(self.user.id, "member")


class GuildMemberUpdate(Member):
    def __del__(self):
        super().create(self.client, self.raw, user=self.user, guild_id=self.guild_id, cache=True)

    @classmethod
    def create(cls, client, resp, *, user=None, guild_id=None, cache: bool = False):
        return super().create(client, resp, user=user, guild_id=guild_id, cache=False)

    @property
    def original(self):
        if self.client.has_cache:
            return self.client.cache.get_guild_container(self.guild_id).get_storage("member").get(self.user.id)


class GuildRoleCreate(EventBase):
    def __init__(self, client, resp: dict):
        super().__init__(client, resp)
        self.guild_id = Snowflake(resp["guild_id"])
        self.role = Role.create(client, resp["role"], guild_id=self.guild_id)

    @property
    def guild(self):
        if self.client.has_cache:
            return self.client.get(self.guild_id, "guild")


class GuildRoleUpdate(EventBase):
    def __init__(self, client, resp: dict):
        super().__init__(client, resp)
        self.guild_id = Snowflake(resp["guild_id"])
        self.role = Role(client, resp["role"], guild_id=self.guild_id)

    def __del__(self):
        Role.create(self.client, self.raw["role"], guild_id=self.guild_id)

    @property
    def guild(self):
        if self.client.has_cache:
            return self.client.get(self.guild_id, "guild")

    @property
    def original(self):
        if self.client.has_cache:
            return self.guild.get(self.role.id, "role")


class GuildRoleDelete(EventBase):
    def __init__(self, client, resp: dict):
        super().__init__(client, resp)
        self.guild_id = Snowflake(resp["guild_id"])
        self.role_id = Snowflake(resp["role_id"])

    def __del__(self):
        if self.client.has_cache:
            self.client.cache.remove(self.role_id, "role")

    @property
    def guild(self):
        if self.client.has_cache:
            return self.client.get(self.guild_id, "guild")

    @property
    def role(self):
        if self.client.has_cache:
            return self.guild.get(self.role_id, "role")


InteractionCreate = Interaction


class InviteCreate(EventBase):
    def __init__(self, client, resp: dict):
        super().__init__(client, resp)
        self.channel_id = Snowflake(resp["channel_id"])
        self.code = resp["code"]
        self.created_at = datetime.datetime.fromisoformat(resp["created_at"])
        self.guild_id = Snowflake.optional(resp.get("guild_id"))
        self.__inviter = resp.get("inviter")
        self.inviter = User.create(client, self.__inviter) if self.__inviter else self.__inviter
        self.max_age = resp["max_age"]
        self.max_uses = resp["max_uses"]
        self.target_type = resp.get("target_type")
        self.__target_user = resp.get("target_user")
        self.target_user = User.create(client, self.__target_user) if self.__target_user else self.__target_user
        self.target_application = resp.get("target_application")
        self.temporary = resp["temporary"]
        self.uses = resp["uses"]

    @property
    def channel(self):
        if self.client.has_cache:
            return self.client.get(self.channel_id, "channel")

    @property
    def guild(self):
        if self.guild_id and self.client.has_cache:
            return self.client.get(self.guild_id, "guild")


class InviteDelete(EventBase):
    def __init__(self, client, resp: dict):
        super().__init__(client, resp)
        self.channel_id = Snowflake(resp["channel_id"])
        self.code = resp["code"]
        self.guild_id = Snowflake.optional(resp.get("guild_id"))

    @property
    def channel(self):
        if self.client.has_cache:
            return self.client.get(self.channel_id, "channel")

    @property
    def guild(self):
        if self.guild_id and self.client.has_cache:
            return self.client.get(self.guild_id, "guild")


MessageCreate = Message


class MessageUpdate(Message):
    def __del__(self):
        Message.create(self.client, self.raw, guild_id=self.guild_id)

    @classmethod
    def create(cls, client, resp, **kwargs):
        try:
            return cls(client, resp, **kwargs)
        except KeyError:
            if client.has_cache:
                msg = client.get(resp["id"])
                if msg:
                    orig = msg.raw
                    for k, v in resp.items():
                        if orig.get(k) != v:
                            orig[k] = v
                    ret = cls(client, orig, **kwargs)
                    ret._dont_dispatch = True
                    return ret

    @property
    def original(self):
        if self.client.has_cache:
            return self.client.get(self.id, "message")


class MessageDelete(EventBase):
    def __init__(self, client, resp: dict):
        super().__init__(client, resp)
        self.id = Snowflake(resp["id"])
        self.channel_id = Snowflake(resp["channel_id"])
        self.guild_id = Snowflake.optional(resp.get("guild_id"))

    def __del__(self):
        if self.client.has_cache:
            self.client.cache.remove(self.id, "message")

    @property
    def message(self):
        if self.client.has_cache:
            return self.client.get(self.id, "message")

    @property
    def channel(self):
        if self.client.has_cache:
            return self.client.get(self.channel_id, "channel")

    @property
    def guild(self):
        if self.guild_id and self.client.has_cache:
            return self.client.get(self.guild_id, "guild")


class MessageDeleteBulk(EventBase):
    def __init__(self, client, resp: dict):
        super().__init__(client, resp)
        self.ids = [Snowflake(x) for x in resp["ids"]]
        self.channel_id = Snowflake(resp["channel_id"])
        self.guild_id = Snowflake.optional(resp.get("guild_id"))

    def __del__(self):
        if self.client.has_cache:
            [self.client.cache.remove(x.id, "message") for x in self.available_messages]

    @property
    def channel(self):
        if self.client.has_cache:
            return self.client.get(self.channel_id, "channel")

    @property
    def guild(self):
        if self.guild_id and self.client.has_cache:
            return self.client.get(self.guild_id, "guild")

    @property
    def available_messages(self):
        if self.client.has_cache:
            tries = [self.client.get(x, "message") for x in self.ids]
            return [x for x in tries if x]


class MessageReactionAdd(EventBase):
    def __init__(self, client, resp: dict):
        super().__init__(client, resp)
        self.user_id = Snowflake(resp["user_id"])
        self.channel_id = Snowflake(resp["channel_id"])
        self.message_id = Snowflake(resp["message_id"])
        self.guild_id = Snowflake.optional(resp.get("guild_id"))
        self.__member = resp.get("member")
        self.member = Member.create(client, self.__member, guild_id=self.guild_id)
        self.emoji = Emoji(client, resp["emoji"])

    @property
    def user(self):
        if self.client.has_cache:
            return self.client.get(self.user_id, "user")

    @property
    def channel(self):
        if self.client.has_cache:
            return self.client.get(self.channel_id, "channel")

    @property
    def message(self):
        if self.client.has_cache:
            return self.client.get(self.message_id, "message")

    @property
    def guild(self):
        if self.guild_id and self.client.has_cache:
            return self.client.get(self.guild_id, "guild")


class MessageReactionRemove(EventBase):
    def __init__(self, client, resp: dict):
        super().__init__(client, resp)
        self.user_id = Snowflake(resp["user_id"])
        self.channel_id = Snowflake(resp["channel_id"])
        self.message_id = Snowflake(resp["message_id"])
        self.guild_id = Snowflake.optional(resp.get("guild_id"))
        self.emoji = Emoji(client, resp["emoji"])

    @property
    def user(self):
        if self.client.has_cache:
            return self.client.get(self.user_id, "user")

    @property
    def channel(self):
        if self.client.has_cache:
            return self.client.get(self.channel_id, "channel")

    @property
    def message(self):
        if self.client.has_cache:
            return self.client.get(self.message_id, "message")

    @property
    def guild(self):
        if self.guild_id and self.client.has_cache:
            return self.client.get(self.guild_id, "guild")


class MessageReactionRemoveAll(EventBase):
    def __init__(self, client, resp: dict):
        super().__init__(client, resp)
        self.channel_id = Snowflake(resp["channel_id"])
        self.message_id = Snowflake(resp["message_id"])
        self.guild_id = Snowflake.optional(resp.get("guild_id"))

    @property
    def channel(self):
        if self.client.has_cache:
            return self.client.get(self.channel_id, "channel")

    @property
    def message(self):
        if self.client.has_cache:
            return self.client.get(self.message_id, "message")

    @property
    def guild(self):
        if self.guild_id and self.client.has_cache:
            return self.client.get(self.guild_id, "guild")


class MessageReactionRemoveEmoji(EventBase):
    def __init__(self, client, resp: dict):
        super().__init__(client, resp)
        self.channel_id = Snowflake(resp["channel_id"])
        self.message_id = Snowflake(resp["message_id"])
        self.guild_id = Snowflake.optional(resp.get("guild_id"))
        self.emoji = Emoji(client, resp["emoji"])

    @property
    def channel(self):
        if self.client.has_cache:
            return self.client.get(self.channel_id, "channel")

    @property
    def message(self):
        if self.client.has_cache:
            return self.client.get(self.message_id, "message")

    @property
    def guild(self):
        if self.guild_id and self.client.has_cache:
            return self.client.get(self.guild_id, "guild")


class PresenceUpdate(EventBase):
    def __init__(self, client, resp: dict):
        super().__init__(client, resp)
        self.user = User.create(self.client, resp["user"])
        self.guild_id = Snowflake(resp["guild_id"])
        self.status = resp["status"]
        self.activities = [Activity(x) for x in resp["activities"]]
        self.client_status = resp["client_status"]

    @property
    def guild(self):
        if self.client.has_cache:
            return self.client.cache.get(self.guild_id, "guild")


class TypingStart(EventBase):
    def __init__(self, client, resp: dict):
        super().__init__(client, resp)
        self.channel_id = Snowflake(resp["channel_id"])
        self.guild_id = Snowflake.optional(resp.get("guild_id"))
        self.user_id = Snowflake(resp["user_id"])
        self.timestamp = datetime.datetime.fromtimestamp(resp["timestamp"])

    @property
    def channel(self):
        if self.client.has_cache:
            return self.client.get(self.channel_id, "channel")

    @property
    def guild(self):
        if self.guild_id and self.client.has_cache:
            return self.client.get(self.guild_id, "guild")

    @property
    def user(self):
        if self.client.has_cache:
            return self.client.get(self.user_id, "user")


class UserUpdate(User):
    def __del__(self):
        User.create(self.client, self.raw)

    @classmethod
    def create(cls, client, resp, **kwargs):
        return cls(client, resp)

    @property
    def original(self):
        if self.client.has_cache:
            return self.client.get(self.id, "guild")


VoiceStateUpdate = VoiceState
