import typing
from .commands import ApplicationCommandInteractionDataOption, ApplicationCommandTypes
from .components import Component, ComponentTypes
from ..channel import Channel, Message, Embed, AllowedMentions
from ..guild import GuildMember
from ..permission import Role
from ..snowflake import Snowflake
from ..user import User
from ...base.model import TypeBase, FlagBase


class Interaction:
    TYPING = typing.Union[int, str, Snowflake, "Interaction"]

    def __init__(self, client, resp):
        self.raw = resp
        self.client = client
        self.id = Snowflake(resp["id"])
        self.application_id = Snowflake(resp["application_id"])
        self.type = InteractionRequestType(resp["type"])
        self.data = InteractionData(client, resp.get("data")) if "data" in resp else resp.get("data")
        self.guild_id = Snowflake(resp.get("guild_id"))
        self.channel_id = Snowflake(resp.get("channel_id"))
        self.__member = resp.get("member")
        self.member = GuildMember.create(client, self.__member, guild_id=self.guild_id) if self.__member else None
        self.__user = resp.get("user")
        self.user = User.create(client, self.__user) if self.__user else None
        self.token = resp["token"]
        self.version = resp["version"]
        self.__message = resp.get("message")
        self._message = Message.create(client, self.__message) if self.__message else self.__message

    def __int__(self):
        return int(self.id)

    def create_response(self, interaction_response):
        return self.client.create_interaction_response(self, interaction_response)

    def create_followup_message(self, **kwargs):
        return self.client.create_followup_message(self, **kwargs)

    @property
    def message(self):
        if self.type.application_command:
            raise AttributeError("message is exclusive to Components.")
        return self._message

    @property
    def target(self):
        if not self.type.application_command or self.data.type.chat_input:
            raise AttributeError("target is exclusive to context menu.")
        return self.data.resolved.get(self.data.target_id)

    @classmethod
    def create(cls, client, resp):
        return cls(client, resp)


class InteractionRequestType(TypeBase):
    PING = 1
    APPLICATION_COMMAND = 2
    MESSAGE_COMPONENT = 3


class InteractionData:
    def __init__(self, client, resp: dict):
        self.id = Snowflake.optional(resp.get("id"))
        self.name = resp.get("name")
        self.type = ApplicationCommandTypes(resp.get("type")) if resp.get("type") is not None else None
        self.__resolved = resp.get("resolved")
        self.resolved = ResolvedData(client, resp.get("resolved")) if self.__resolved else self.__resolved
        self.options = [ApplicationCommandInteractionDataOption(x) for x in resp.get("options", [])]
        self.custom_id = resp.get("custom_id")
        self.component_type = ComponentTypes(resp.get("component_type")) if resp.get("component_type") is not None else None
        self.values = resp.get("values", [])
        self.target_id = Snowflake.optional(resp.get("target_id"))


class ResolvedData:
    def __init__(self, client, resp: dict):
        self.users = {Snowflake(k): User.create(client, v) for k, v in resp.get("users", {}).items()}
        self.__users = {x: Snowflake(x) for x in resp.get("users", {})}
        self.members = {Snowflake(k): GuildMember.create(client, v, user=self.users.get(self.__users.get(k))) for k, v in resp.get("members", {}).items()}
        self.roles = {Snowflake(k): Role.create(client, v) for k, v in resp.get("roles", {}).items()}
        self.channels = {Snowflake(k): Channel.create(client, v) for k, v in resp.get("channels", {}).items()}
        self.messages = {Snowflake(k): Message.create(client, v) for k, v in resp.get("messages", {}).items()}

    def get(self, value: typing.Union[int, str, Snowflake]):
        value = Snowflake.ensure_snowflake(value)
        for x in [self.members, self.users, self.roles, self.channels, self.messages]:
            if value in x:
                return x.get(value)
        return value


class MessageInteraction:
    def __init__(self, client, resp):
        self.id = Snowflake(resp["id"])
        self.type = InteractionRequestType(resp["type"])
        self.name = resp["name"]
        self.user = User.create(client, resp["user"])


class InteractionResponse:
    def __init__(self, callback_type: typing.Union[int, "InteractionCallbackType"], data: typing.Union[dict, "InteractionApplicationCommandCallbackData"]):
        self.type = callback_type
        self.data = data

    def to_dict(self):
        return {"type": int(self.type), "data": self.data if isinstance(self.data, dict) else self.data.to_dict()}


class InteractionCallbackType(TypeBase):
    PONG = 1
    CHANNEL_MESSAGE_WITH_SOURCE = 4
    DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE = 5
    DEFERRED_UPDATE_MESSAGE = 6
    UPDATE_MESSAGE = 7


class InteractionApplicationCommandCallbackData:
    def __init__(self, *,
                 tts: bool = None,
                 content: str = None,
                 embeds: typing.List[Embed] = None,
                 allowed_mentions: AllowedMentions = None,
                 flags: typing.Union["InteractionApplicationCommandCallbackDataFlags", int] = None,
                 components: typing.List[typing.Union[dict, Component]] = None):
        self.tts = tts
        self.content = content
        self.embeds = embeds
        self.allowed_mentions = allowed_mentions
        self.flags = InteractionApplicationCommandCallbackDataFlags.from_value(flags) if isinstance(flags, int) else flags
        self.components = components

    def to_dict(self):
        ret = {}
        if self.tts is not None:
            ret["tts"] = self.tts
        if self.content is not None:
            ret["content"] = self.content
        if self.embeds is not None:
            ret["embeds"] = [x.to_dict() for x in self.embeds]
        if self.allowed_mentions is not None:
            ret["allowed_mentions"] = self.allowed_mentions.to_dict()
        if self.flags is not None:
            ret["flags"] = int(self.flags)
        if self.components is not None:
            ret["components"] = [x if isinstance(x, dict) else x.to_dict() for x in self.components]
        return ret


class InteractionApplicationCommandCallbackDataFlags(FlagBase):
    EPHEMERAL = 1 << 6
