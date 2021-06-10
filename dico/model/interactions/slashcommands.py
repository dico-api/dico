from ..channel import Channel
from ..guild import Member
from ..permission import Role
from ..snowflake import Snowflake
from ..user import User
from ...base.model import TypeBase


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
