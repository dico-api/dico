import typing

from ..channel import Channel, Embed, AllowedMentions
from ..guild import Member
from ..permission import Role
from ..snowflake import Snowflake
from ..user import User
from ...base.model import TypeBase, FlagBase


class ApplicationCommand:
    def __init__(self, resp: dict, command_creation: bool = False):
        self.id = Snowflake(resp["id"])
        self.application_id = Snowflake(resp["application_id"])
        self.name = resp["name"]
        self.description = resp["description"]
        self.options = [ApplicationCommandOption(x) for x in resp.get("options", [])]
        self.default_permission = resp.get("default_permission", True)
        self.__command_creation = command_creation

    def to_dict(self):
        if self.__command_creation:
            return {"name": self.name, "description": self.description, "options": [x.to_dict() for x in self.options], "default_permission": self.default_permission}
        return {"id": self.id, "application_id": self.application_id, "name": self.name,
                "description": self.description, "options": self.options, "default_permission": self.default_permission}

    @classmethod
    def create(cls, name, description, options, default_permission):
        return cls({"name": name, "description": description, "options": options, "default_permission": default_permission}, command_creation=True)


class ApplicationCommandOption:
    def __init__(self, resp: dict):
        self.type = ApplicationCommandOptionType(resp["type"])
        self.application_id = Snowflake(resp["application_id"])
        self.name = resp["name"]
        self.description = resp["description"]
        self.required = resp.get("required", False)
        self.choices = [ApplicationCommandOptionChoice(x) for x in resp.get("choices", [])]
        self.options = [ApplicationCommandOption(x) for x in resp.get("options", [])]

    def to_dict(self):
        ret = {"type": self.type, "application_id": self.application_id, "name": self.name, "description": self.description,
               "required": self.required, "choices": [x.to_dict() for x in self.choices], "options": [x.to_dict() for x in self.options]}
        if not ret["options"]:
            del ret["options"]
        if not ret["choices"]:
            del ret["choices"]
        return ret


class ApplicationCommandOptionType(TypeBase):
    SUB_COMMAND = 1
    SUB_COMMAND_GROUP = 2
    STRING = 3
    INTEGER = 4
    BOOLEAN = 5
    USER = 6
    CHANNEL = 7
    ROLE = 8


class ApplicationCommandOptionChoice:
    def __init__(self, resp: dict):
        self.name = resp["name"]
        self.value = resp["value"]

    def to_dict(self):
        return {"name": self.name, "value": self.value}

    @classmethod
    def create(cls, name, value):
        return cls({"name": name, "value": value})


class GuildApplicationCommandPermissions:
    def __init__(self, resp: dict):
        self.id = Snowflake(resp["id"])
        self.application_id = Snowflake(resp["application_id"])
        self.guild_id = Snowflake(resp["guild_id"])
        self.permissions = [ApplicationCommandPermissions(x) for x in resp["permissions"]]


class ApplicationCommandPermissions:
    def __init__(self, resp: dict):
        self.id = Snowflake(resp["id"])
        self.type = ApplicationCommandPermissionType(resp["type"])
        self.permission = resp["permission"]


class ApplicationCommandPermissionType(TypeBase):
    ROLE = 1
    USER = 2


class Interaction:
    def __init__(self, client, resp):
        self.client = client
        self.id = Snowflake(resp["id"])
        self.application_id = Snowflake(resp["application_id"])
        self.type = InteractionType(resp["type"])
        self.data = ApplicationCommandInteractionData(client, resp.get("data"))
        self.guild_id = Snowflake(resp.get("guild_id"))
        self.channel_id = Snowflake(resp.get("channel_id"))
        self.__member = resp.get("member")
        self.member = Member.create(client, self.__member, guild_id=self.guild_id) if self.__member else None
        self.__user = resp.get("user")
        self.user = User.create(client, self.__user) if self.__user else None
        self.token = resp["token"]
        self.version = resp["version"]

    def create_response(self, interaction_response):
        return self.client.create_interaction_response(self, interaction_response)

    @classmethod
    def create(cls, client, resp):
        return cls(client, resp)


class InteractionType(TypeBase):
    PING = 1
    APPLICATION_COMMAND = 2


class ApplicationCommandInteractionData:
    def __init__(self, client, resp: dict):
        self.id = Snowflake(resp["id"])
        self.name = resp["name"]
        self.__resolved = resp.get("resolved")
        self.resolved = ApplicationCommandInteractionDataResolved(client, resp.get("resolved")) if self.__resolved else self.__resolved
        self.options = resp.get("options")


class ApplicationCommandInteractionDataResolved:
    def __init__(self, client, resp: dict):
        self.users = [User.create(client, x) for x in resp.get("users", {}).values()]
        self.members = [Member.create(client, x) for x in resp.get("members", {}).values()]
        self.roles = [Role.create(client, x) for x in resp.get("roles", {}).values()]
        self.channels = [Channel.create(client, x) for x in resp.get("channels", {}).values()]


class ApplicationCommandInteractionDataOption:
    def __init__(self, resp):
        self.name = resp["name"]
        self.type = ApplicationCommandOptionType(resp["type"])
        self.value = resp.get("value")
        self.options = [ApplicationCommandInteractionDataOption(x) for x in resp.get("options", [])]


class InteractionCallbackType(TypeBase):
    PONG = 1
    CHANNEL_MESSAGE_WITH_SOURCE = 4
    DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE = 5


class InteractionCallbackFlags(FlagBase):
    # This actually still doesn't exist.
    EPHEMERAL = 64


class InteractionApplicationCommandCallbackData:
    def __init__(self, *,
                 tts: bool = None,
                 content: str = None,
                 embeds: typing.List[Embed] = None,
                 allowed_mentions: AllowedMentions = None,
                 flags: int = None):
        self.tts = tts
        self.content = content
        self.embeds = embeds
        self.allowed_mentions = allowed_mentions
        self.flags = flags

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
        return ret


class InteractionResponse:
    def __init__(self, callback_type: typing.Union[int, InteractionCallbackType], data: InteractionApplicationCommandCallbackData):
        self.type = callback_type
        self.data = data

    def to_dict(self):
        return {"type": int(self.type), "data": self.data.to_dict()}


class MessageInteraction:
    def __init__(self, client, resp):
        self.id = Snowflake(resp["id"])
        self.type = InteractionType(resp["type"])
        self.name = resp["name"]
        self.user = User.create(client, resp["user"])
