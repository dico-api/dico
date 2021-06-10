import typing
from .slashcommands import ApplicationCommandInteractionDataResolved
from .components import Component, ComponentTypes
from ..channel import Embed, AllowedMentions
from ..guild import Member
from ..snowflake import Snowflake
from ..user import User
from ...base.model import TypeBase, FlagBase


class Interaction:
    def __init__(self, client, resp):
        self.client = client
        self.id = Snowflake(resp["id"])
        self.application_id = Snowflake(resp["application_id"])
        self.type = InteractionType(resp["type"])
        self.data = ApplicationCommandInteractionData(client, resp.get("data")) if self.type.application_command else resp.get("data")
        self.guild_id = Snowflake(resp.get("guild_id"))
        self.channel_id = Snowflake(resp.get("channel_id"))
        self.__member = resp.get("member")
        self.member = Member.create(client, self.__member, guild_id=self.guild_id) if self.__member else None
        self.__user = resp.get("user")
        self.user = User.create(client, self.__user) if self.__user else None
        self.token = resp["token"]
        self.version = resp["version"]

    def __int__(self):
        return int(self.id)

    def create_response(self, interaction_response):
        return self.client.create_interaction_response(self, interaction_response)

    def create_followup_message(self, **kwargs):
        return self.client.create_followup_message(self, **kwargs)

    @classmethod
    def create(cls, client, resp):
        return cls(client, resp)


class InteractionType(TypeBase):
    PING = 1
    APPLICATION_COMMAND = 2
    MESSAGE_COMPONENT = 3


class ApplicationCommandInteractionData:
    def __init__(self, client, resp: dict):
        self.id = Snowflake(resp["id"])
        self.name = resp["name"]
        self.__resolved = resp.get("resolved")
        self.resolved = ApplicationCommandInteractionDataResolved(client, resp.get("resolved")) if self.__resolved else self.__resolved
        self.options = resp.get("options")
        self.custom_id = resp.get("custom_id")
        self.component_type = ComponentTypes(resp.get("component_type")) if resp.get("component_type") else None


class InteractionCallbackType(TypeBase):
    PONG = 1
    CHANNEL_MESSAGE_WITH_SOURCE = 4
    DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE = 5
    DEFERRED_UPDATE_MESSAGE = 6
    UPDATE_MESSAGE = 7


class InteractionCallbackFlags(FlagBase):
    # This actually still doesn't exist.
    EPHEMERAL = 64


class InteractionApplicationCommandCallbackData:
    def __init__(self, *,
                 tts: bool = None,
                 content: str = None,
                 embeds: typing.List[Embed] = None,
                 allowed_mentions: AllowedMentions = None,
                 flags: int = None,
                 components: typing.List[typing.Union[dict, Component]] = None):
        self.tts = tts
        self.content = content
        self.embeds = embeds
        self.allowed_mentions = allowed_mentions
        self.flags = flags
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


class InteractionResponse:
    def __init__(self, callback_type: typing.Union[int, InteractionCallbackType], data: typing.Union[dict, InteractionApplicationCommandCallbackData]):
        self.type = callback_type
        self.data = data

    def to_dict(self):
        return {"type": int(self.type), "data": self.data if isinstance(self.data, dict) else self.data.to_dict()}


class MessageInteraction:
    def __init__(self, client, resp):
        self.id = Snowflake(resp["id"])
        self.type = InteractionType(resp["type"])
        self.name = resp["name"]
        self.user = User.create(client, resp["user"])
