import sys
import typing
import datetime
from .application import Application
from .channel import Channel, Message, ThreadMember
from .emoji import Emoji
from .gateway import Activity
from .guild import Guild, GuildMember, Integration
from .guild_scheduled_event import GuildScheduledEvent
from .invite import InviteTargetTypes
from .permission import Role
from .snowflake import Snowflake
from .stage import StageInstance
from .sticker import Sticker
from .user import User
from .voice import VoiceState
from .interactions import Interaction  # , ApplicationCommand, ApplicationCommandOption
from ..base.model import EventBase

if typing.TYPE_CHECKING:
    from ..client import Client


class Ready(EventBase):
    def __init__(self, client: "Client", resp: dict):
        super().__init__(client, resp)
        self.v: int = resp["v"]
        self.user: User = User.create(client, resp["user"])
        self.guilds: typing.List[dict] = resp["guilds"]
        self.session_id: str = resp["session_id"]
        self.shard: typing.Optional[typing.List[int]] = resp.get("shard")
        self.application: dict = resp["application"]

    @property
    def application_id(self) -> Snowflake:
        return Snowflake(self.application["id"])

    @property
    def guild_count(self) -> int:
        return len(self.guilds)

    @property
    def shard_id(self):
        if self.shard:
            return self.shard[0]


"""
class ApplicationCommandCreate(ApplicationCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = kwargs.get("client")
        self.guild_id = Snowflake.optional(kwargs.get("guild_id"))

    @classmethod
    def create(cls, client, resp):  # noqa
        resp["client"] = client
        resp["options"] = [ApplicationCommandOption.create(x) for x in resp.pop("options", [])]
        resp["command_type"] = resp.pop("type", 1)
        return cls(**resp)


ApplicationCommandUpdate = ApplicationCommandCreate
ApplicationCommandDelete = ApplicationCommandCreate
"""

# TODO: refactor update/delete objects

ChannelCreate = Channel


class ChannelUpdate(Channel):
    def __del__(self):
        Channel.create(self.client, self.raw)

    @classmethod
    def create(cls, client: "Client", resp: dict, **kwargs):
        return cls(client, resp, **kwargs)

    @property
    def original(self) -> typing.Optional[Channel]:
        if self.client.has_cache:
            return self.client.get(self.id, "channel")


class ChannelDelete(Channel):
    def __del__(self):
        if self.client.has_cache:
            self.client.cache.remove(self.id, self._cache_type)


class ChannelPinsUpdate(EventBase):
    def __init__(self, client: "Client", resp: dict):
        super().__init__(client, resp)
        self.guild_id: typing.Optional[Snowflake] = Snowflake.optional(resp.get("guild_id"))
        self.channel_id: Snowflake = Snowflake(resp["channel_id"])
        self.__last_pin_timestamp = resp.get("last_pin_timestamp")
        self.last_pin_timestamp: typing.Optional[datetime.datetime] = datetime.datetime.fromisoformat(self.__last_pin_timestamp) \
            if self.__last_pin_timestamp else self.__last_pin_timestamp

    @property
    def channel(self) -> typing.Optional[Channel]:
        if self.client.has_cache:
            return self.client.get(self.channel_id, "channel")

    @property
    def guild(self) -> typing.Optional[Guild]:
        if self.guild_id:
            return self.client.get(self.guild_id, "guild")


ThreadCreate = Channel
ThreadUpdate = ChannelUpdate
ThreadDelete = ChannelDelete


class ThreadListSync(EventBase):
    def __init__(self, client: "Client", resp: dict):
        super().__init__(client, resp)
        self.guild_id: Snowflake = Snowflake(resp["guild_id"])
        self.channel_ids: typing.List[Snowflake] = [Snowflake(x) for x in resp.get("channel_ids", [])]
        self.threads: typing.List[Channel] = [Channel.create(client, x) for x in resp["threads"]]
        self.members: typing.List[ThreadMember] = [ThreadMember(client, x) for x in resp["members"]]

    @property
    def guild(self) -> typing.Optional[Guild]:
        if self.guild_id:
            return self.client.get(self.guild_id, "guild")

    @property
    def channels(self) -> typing.Optional[typing.List[Channel]]:
        if self.client.has_cache:
            return [self.client.get(x, "channel") for x in self.channel_ids]


ThreadMemberUpdate = ThreadMember


class ThreadMembersUpdate(EventBase):
    def __init__(self, client: "Client", resp: dict):
        super().__init__(client, resp)
        self.id: Snowflake = Snowflake(resp["id"])
        self.guild_id: Snowflake = Snowflake(resp["guild_id"])
        self.member_count: int = resp["member_count"]
        self.added_members: typing.Optional[typing.List[ThreadMember]] = [ThreadMember(client, x) for x in resp.get("added_members", [])]
        self.removed_member_ids: typing.Optional[typing.List[Snowflake]] = [Snowflake(x) for x in resp.get("removed_member_ids", [])]

    @property
    def thread(self) -> typing.Optional[Channel]:
        if self.client.has_cache:
            return self.client.get(self.id, "channel")

    @property
    def guild(self) -> typing.Optional[Guild]:
        if self.guild_id:
            return self.client.get(self.guild_id, "guild")


class GuildCreate(Guild):
    @classmethod
    def create(cls, client: "Client", resp: dict, **kwargs):
        kwargs.setdefault("ensure_cache_type", "guild")
        if "name" not in resp:
            print(f"Invalid payload warning! Full payload: {resp}", file=sys.stderr)
            return None
        return super().create(client, resp, **kwargs)


class GuildUpdate(Guild):
    def __del__(self):
        Guild.create(self.client, self.raw, ensure_cache_type="guild")

    @classmethod
    def create(cls, client, resp, **kwargs):
        return cls(client, resp)

    @property
    def original(self) -> typing.Optional[Guild]:
        if self.client.has_cache:
            return self.client.get(self.id, "guild")


class GuildDelete(GuildCreate):
    def __del__(self):
        if self.client.has_cache:
            self.client.cache.remove(self.id, self._cache_type)


class GuildBanAdd(EventBase):
    def __init__(self, client: "Client", resp: dict):
        super().__init__(client, resp)
        self.guild_id: Snowflake = Snowflake(resp["guild_id"])
        self.user: User = User.create(self.client, resp["user"])

    @property
    def guild(self) -> typing.Optional[Guild]:
        if self.client.has_cache:
            return self.client.get(self.guild_id, "guild")


class GuildBanRemove(GuildBanAdd):
    pass


class GuildEmojisUpdate(EventBase):
    def __init__(self, client: "Client", resp: dict):
        super().__init__(client, resp)
        self.guild_id: Snowflake = Snowflake(resp["guild_id"])
        self.emojis: typing.List[Emoji] = [Emoji(self.client, x) for x in resp["emojis"]]

    @property
    def guild(self) -> typing.Optional[Guild]:
        if self.client.has_cache:
            return self.client.get(self.guild_id, "guild")


class GuildStickersUpdate(EventBase):
    def __init__(self, client: "Client", resp: dict):
        super().__init__(client, resp)
        self.guild_id: Snowflake = Snowflake(resp["guild_id"])
        self.stickers: typing.List[Sticker] = [Sticker.create(client, x) for x in resp["stickers"]]

    @property
    def guild(self) -> typing.Optional[Guild]:
        if self.client.has_cache:
            return self.client.get(self.guild_id, "guild")


class GuildIntegrationsUpdate(EventBase):
    def __init__(self, client: "Client", resp: dict):
        super().__init__(client, resp)
        self.guild_id: Snowflake = Snowflake(resp["guild_id"])

    @property
    def guild(self) -> typing.Optional[Guild]:
        if self.client.has_cache:
            return self.client.get(self.guild_id, "guild")


GuildMemberAdd = GuildMember


class GuildMemberRemove(EventBase):
    def __init__(self, client: "Client", resp: dict):
        super().__init__(client, resp)
        self.guild_id: Snowflake = Snowflake(resp["guild_id"])
        self.user: User = User.create(self.client, resp["user"])

    def __del__(self):
        if self.client.has_cache:
            self.guild.cache.remove(self.user.id, "member")

    @property
    def guild(self) -> typing.Optional[Guild]:
        if self.client.has_cache:
            return self.client.get(self.guild_id, "guild")

    @property
    def member(self) -> typing.Optional[GuildMember]:
        if self.client.has_cache:
            return self.guild.get(self.user.id, "member")


class GuildMemberUpdate(GuildMember):
    def __del__(self):
        super().create(self.client, self.raw, user=self.user, guild_id=self.guild_id, cache=True)

    @classmethod
    def create(cls, client: "Client", resp: dict, *, user=None, guild_id=None, cache: bool = False):
        return super().create(client, resp, user=user, guild_id=guild_id, cache=False)

    @property
    def original(self) -> typing.Optional[GuildMember]:
        if self.client.has_cache:
            return self.client.cache.get_guild_container(self.guild_id).get_storage("member").get(self.user.id)


class GuildRoleCreate(EventBase):
    def __init__(self, client: "Client", resp: dict):
        super().__init__(client, resp)
        self.guild_id: Snowflake = Snowflake(resp["guild_id"])
        self.role: Role = Role.create(client, resp["role"], guild_id=self.guild_id)

    @property
    def guild(self) -> typing.Optional[Guild]:
        if self.client.has_cache:
            return self.client.get(self.guild_id, "guild")


class GuildRoleUpdate(EventBase):
    def __init__(self, client: "Client", resp: dict):
        super().__init__(client, resp)
        self.guild_id: Snowflake = Snowflake(resp["guild_id"])
        self.role: Role = Role(client, resp["role"], guild_id=self.guild_id)

    def __del__(self):
        Role.create(self.client, self.raw["role"], guild_id=self.guild_id)

    @property
    def guild(self) -> typing.Optional[Guild]:
        if self.client.has_cache:
            return self.client.get(self.guild_id, "guild")

    @property
    def original(self) -> typing.Optional[Role]:
        if self.client.has_cache:
            return self.guild.get(self.role.id, "role")


class GuildRoleDelete(EventBase):
    def __init__(self, client: "Client", resp: dict):
        super().__init__(client, resp)
        self.guild_id: Snowflake = Snowflake(resp["guild_id"])
        self.role_id: Snowflake = Snowflake(resp["role_id"])

    def __del__(self):
        if self.client.has_cache:
            self.client.cache.remove(self.role_id, "role")

    @property
    def guild(self) -> typing.Optional[Guild]:
        if self.client.has_cache:
            return self.client.get(self.guild_id, "guild")

    @property
    def role(self) -> typing.Optional[Role]:
        if self.client.has_cache:
            return self.guild.get(self.role_id, "role")


GuildScheduledEventCreate = GuildScheduledEvent
GuildScheduledEventUpdate = GuildScheduledEvent
GuildScheduledEventDelete = GuildScheduledEvent


class IntegrationCreate(Integration):
    def __init__(self, client: "Client", resp: dict):
        super().__init__(client, resp)
        self.guild_id: Snowflake = Snowflake(resp["guild_id"])

    @property
    def guild(self) -> typing.Optional[Guild]:
        if self.client.has_cache:
            return self.client.cache.get(self.guild_id, "guild")

    @classmethod
    def create(cls, client, resp: dict):
        return cls(client, resp)


IntegrationUpdate = IntegrationCreate


class IntegrationDelete(EventBase):
    def __init__(self, client: "Client", resp: dict):
        super().__init__(client, resp)
        self.id: Snowflake = Snowflake(resp["id"])
        self.guild_id: Snowflake = Snowflake(resp["guild_id"])
        self.application_id: typing.Optional[Snowflake] = Snowflake.optional(resp.get("application_id"))

    @property
    def guild(self) -> typing.Optional[Guild]:
        if self.client.has_cache:
            return self.client.cache.get(self.guild_id, "guild")


InteractionCreate = Interaction


class InviteCreate(EventBase):
    def __init__(self, client: "Client", resp: dict):
        super().__init__(client, resp)
        self.channel_id: Snowflake = Snowflake(resp["channel_id"])
        self.code: str = resp["code"]
        self.created_at: datetime.datetime = datetime.datetime.fromisoformat(resp["created_at"])
        self.guild_id: typing.Optional[Snowflake] = Snowflake.optional(resp.get("guild_id"))
        self.__inviter = resp.get("inviter")
        self.inviter: typing.Optional[User] = User.create(client, self.__inviter) if self.__inviter else self.__inviter
        self.max_age: int = resp["max_age"]
        self.max_uses: int = resp["max_uses"]
        self.__target_type = resp.get("target_type")
        self.target_type: typing.Optional[InviteTargetTypes] = InviteTargetTypes(self.__target_type) if self.__target_type else self.__target_type
        self.__target_user = resp.get("target_user")
        self.target_user: typing.Optional[User] = User.create(client, self.__target_user) if self.__target_user else self.__target_user
        self.__target_application = resp.get("target_application")
        self.target_application: typing.Optional[Application] = Application(client, self.__target_application) if self.__target_application else self.__target_application
        self.temporary: bool = resp["temporary"]
        self.uses: int = resp["uses"]

    @property
    def channel(self) -> typing.Optional[Channel]:
        if self.client.has_cache:
            return self.client.get(self.channel_id, "channel")

    @property
    def guild(self) -> typing.Optional[Guild]:
        if self.guild_id and self.client.has_cache:
            return self.client.get(self.guild_id, "guild")


class InviteDelete(EventBase):
    def __init__(self, client: "Client", resp: dict):
        super().__init__(client, resp)
        self.channel_id: Snowflake = Snowflake(resp["channel_id"])
        self.code: str = resp["code"]
        self.guild_id: typing.Optional[Snowflake] = Snowflake.optional(resp.get("guild_id"))

    @property
    def channel(self) -> typing.Optional[Channel]:
        if self.client.has_cache:
            return self.client.get(self.channel_id, "channel")

    @property
    def guild(self) -> typing.Optional[Guild]:
        if self.guild_id and self.client.has_cache:
            return self.client.get(self.guild_id, "guild")


MessageCreate = Message


class MessageUpdate(Message):
    def __del__(self):
        if self.client.has_cache and not self.client.get(self.id, "message"):
            return
        Message.create(self.client, self.raw, guild_id=self.guild_id)

    @classmethod
    def create(cls, client: "Client", resp: dict, **kwargs):
        try:
            return cls(client, resp, **kwargs)
        except KeyError:
            if client.has_cache:
                msg = client.get(resp["id"], cls._cache_type)
                if msg:
                    orig = msg.raw
                    for k, v in resp.items():
                        if orig.get(k) != v:
                            orig[k] = v
                    ret = cls(client, orig, **kwargs)
                    ret._dont_dispatch = True
                    return ret

    @property
    def original(self) -> typing.Optional[Message]:
        if self.client.has_cache:
            return self.client.get(self.id, "message")


class MessageDelete(EventBase):
    def __init__(self, client: "Client", resp: dict):
        super().__init__(client, resp)
        self.id: Snowflake = Snowflake(resp["id"])
        self.channel_id: Snowflake = Snowflake(resp["channel_id"])
        self.guild_id: typing.Optional[Snowflake] = Snowflake.optional(resp.get("guild_id"))

    def __del__(self):
        if self.client.has_cache:
            self.client.cache.remove(self.id, "message")

    @property
    def message(self) -> typing.Optional[Message]:
        if self.client.has_cache:
            return self.client.get(self.id, "message")

    @property
    def channel(self) -> typing.Optional[Channel]:
        if self.client.has_cache:
            return self.client.get(self.channel_id, "channel")

    @property
    def guild(self) -> typing.Optional[Guild]:
        if self.guild_id and self.client.has_cache:
            return self.client.get(self.guild_id, "guild")


class MessageDeleteBulk(EventBase):
    def __init__(self, client: "Client", resp: dict):
        super().__init__(client, resp)
        self.ids: typing.List[Snowflake] = [Snowflake(x) for x in resp["ids"]]
        self.channel_id: Snowflake = Snowflake(resp["channel_id"])
        self.guild_id: typing.Optional[Snowflake] = Snowflake.optional(resp.get("guild_id"))

    def __del__(self):
        if self.client.has_cache:
            [self.client.cache.remove(x.id, "message") for x in self.available_messages]

    @property
    def channel(self) -> typing.Optional[Channel]:
        if self.client.has_cache:
            return self.client.get(self.channel_id, "channel")

    @property
    def guild(self) -> typing.Optional[Guild]:
        if self.guild_id and self.client.has_cache:
            return self.client.get(self.guild_id, "guild")

    @property
    def available_messages(self) -> typing.Optional[typing.List[Message]]:
        if self.client.has_cache:
            tries = [self.client.get(x, "message") for x in self.ids]
            return [x for x in tries if x]


class MessageReactionAdd(EventBase):
    def __init__(self, client: "Client", resp: dict):
        super().__init__(client, resp)
        self.user_id: Snowflake = Snowflake(resp["user_id"])
        self.channel_id: Snowflake = Snowflake(resp["channel_id"])
        self.message_id: Snowflake = Snowflake(resp["message_id"])
        self.guild_id: typing.Optional[Snowflake] = Snowflake.optional(resp.get("guild_id"))
        self.__member = resp.get("member")
        self.member: typing.Optional[GuildMember] = GuildMember.create(client, self.__member, guild_id=self.guild_id)
        self.emoji: Emoji = Emoji(client, resp["emoji"])

    @property
    def user(self) -> typing.Optional[User]:
        if self.client.has_cache:
            return self.client.get(self.user_id, "user")

    @property
    def channel(self) -> typing.Optional[Channel]:
        if self.client.has_cache:
            return self.client.get(self.channel_id, "channel")

    @property
    def message(self) -> typing.Optional[Message]:
        if self.client.has_cache:
            return self.client.get(self.message_id, "message")

    @property
    def guild(self) -> typing.Optional[Guild]:
        if self.guild_id and self.client.has_cache:
            return self.client.get(self.guild_id, "guild")


class MessageReactionRemove(EventBase):
    def __init__(self, client: "Client", resp: dict):
        super().__init__(client, resp)
        self.user_id: Snowflake = Snowflake(resp["user_id"])
        self.channel_id: Snowflake = Snowflake(resp["channel_id"])
        self.message_id: Snowflake = Snowflake(resp["message_id"])
        self.guild_id: typing.Optional[Snowflake] = Snowflake.optional(resp.get("guild_id"))
        self.emoji: Emoji = Emoji(client, resp["emoji"])

    @property
    def user(self) -> typing.Optional[User]:
        if self.client.has_cache:
            return self.client.get(self.user_id, "user")

    @property
    def channel(self) -> typing.Optional[Channel]:
        if self.client.has_cache:
            return self.client.get(self.channel_id, "channel")

    @property
    def message(self) -> typing.Optional[Message]:
        if self.client.has_cache:
            return self.client.get(self.message_id, "message")

    @property
    def guild(self) -> typing.Optional[Guild]:
        if self.guild_id and self.client.has_cache:
            return self.client.get(self.guild_id, "guild")


class MessageReactionRemoveAll(EventBase):
    def __init__(self, client: "Client", resp: dict):
        super().__init__(client, resp)
        self.channel_id: Snowflake = Snowflake(resp["channel_id"])
        self.message_id: Snowflake = Snowflake(resp["message_id"])
        self.guild_id: typing.Optional[Snowflake] = Snowflake.optional(resp.get("guild_id"))

    @property
    def channel(self) -> typing.Optional[Channel]:
        if self.client.has_cache:
            return self.client.get(self.channel_id, "channel")

    @property
    def message(self) -> typing.Optional[Message]:
        if self.client.has_cache:
            return self.client.get(self.message_id, "message")

    @property
    def guild(self) -> typing.Optional[Guild]:
        if self.guild_id and self.client.has_cache:
            return self.client.get(self.guild_id, "guild")


class MessageReactionRemoveEmoji(EventBase):
    def __init__(self, client: "Client", resp: dict):
        super().__init__(client, resp)
        self.channel_id: Snowflake = Snowflake(resp["channel_id"])
        self.message_id: Snowflake = Snowflake(resp["message_id"])
        self.guild_id: typing.Optional[Snowflake] = Snowflake.optional(resp.get("guild_id"))
        self.emoji: Emoji = Emoji(client, resp["emoji"])

    @property
    def channel(self) -> typing.Optional[Channel]:
        if self.client.has_cache:
            return self.client.get(self.channel_id, "channel")

    @property
    def message(self) -> typing.Optional[Message]:
        if self.client.has_cache:
            return self.client.get(self.message_id, "message")

    @property
    def guild(self) -> typing.Optional[Guild]:
        if self.guild_id and self.client.has_cache:
            return self.client.get(self.guild_id, "guild")


class ClientStatus:
    def __init__(self, resp: dict):
        self.desktop: typing.Optional[str] = resp.get("desktop")
        self.mobile: typing.Optional[str] = resp.get("mobile")
        self.web: typing.Optional[str] = resp.get("web")


class PresenceUpdate(EventBase):
    def __init__(self, client: "Client", resp: dict):
        super().__init__(client, resp)
        self.user: User = User.create(self.client, resp["user"])
        self.guild_id: typing.Optional[Snowflake] = Snowflake.optional(resp.get("guild_id"))
        self.status: str = resp["status"]
        self.activities: typing.List[Activity] = [Activity(x) for x in resp["activities"]]
        self.client_status: ClientStatus = ClientStatus(resp["client_status"])

    @property
    def guild(self) -> typing.Optional[Guild]:
        if self.client.has_cache:
            return self.client.cache.get(self.guild_id, "guild")


StageInstanceCreate = StageInstance


class StageInstanceDelete(StageInstance):
    def __del__(self):
        if self.client.has_cache:
            self.client.cache.remove(self.id, self._cache_type)


class StageInstanceUpdate(StageInstance):
    def __del__(self):
        StageInstance.create(self.client, self.raw)

    @classmethod
    def create(cls, client: "Client", resp: dict, **kwargs):
        return cls(client, resp)

    @property
    def original(self) -> typing.Optional[StageInstance]:
        if self.client.has_cache:
            return self.client.get(self.id, "stage_instance")


class TypingStart(EventBase):
    def __init__(self, client: "Client", resp: dict):
        super().__init__(client, resp)
        self.channel_id: Snowflake = Snowflake(resp["channel_id"])
        self.guild_id: typing.Optional[Snowflake] = Snowflake.optional(resp.get("guild_id"))
        self.user_id: Snowflake = Snowflake(resp["user_id"])
        self.timestamp: datetime.datetime = datetime.datetime.fromtimestamp(resp["timestamp"])

    @property
    def channel(self) -> typing.Optional[Channel]:
        if self.client.has_cache:
            return self.client.get(self.channel_id, "channel")

    @property
    def guild(self) -> typing.Optional[Guild]:
        if self.guild_id and self.client.has_cache:
            return self.client.get(self.guild_id, "guild")

    @property
    def user(self) -> typing.Optional[User]:
        if self.client.has_cache:
            return self.client.get(self.user_id, "user")


class UserUpdate(User):
    def __del__(self):
        User.create(self.client, self.raw)

    @classmethod
    def create(cls, client: "Client", resp: dict, **kwargs):
        return cls(client, resp)

    @property
    def original(self) -> typing.Optional[User]:
        if self.client.has_cache:
            return self.client.get(self.id, "user")


VoiceStateUpdate = VoiceState


class VoiceServerUpdate(EventBase):
    def __init__(self, client: "Client", resp: dict):
        super().__init__(client, resp)
        self.token: str = resp["token"]
        self.guild_id: Snowflake = Snowflake(resp["guild_id"])
        self.endpoint: typing.Optional[str] = resp.get("endpoint")

    @property
    def guild(self) -> typing.Optional[Guild]:
        if self.client.has_cache:
            return self.client.get(self.guild_id, "guild")


class WebhooksUpdate(EventBase):
    def __init__(self, client: "Client", resp: dict):
        super().__init__(client, resp)
        self.guild_id: Snowflake = Snowflake(resp["guild_id"])
        self.channel_id: Snowflake = Snowflake(resp["channel_id"])

    @property
    def guild(self) -> typing.Optional[Guild]:
        if self.client.has_cache:
            return self.client.get(self.guild_id, "guild")

    @property
    def channel(self) -> typing.Optional[Channel]:
        if self.client.has_cache:
            return self.client.get(self.channel_id, "channel")
