import typing
from ..permission import Role
from ..snowflake import Snowflake
from ..user import User
from ...base.model import TypeBase


class ApplicationCommand:
    TYPING = typing.Union[int, str, Snowflake, "ApplicationCommand"]
    RESPONSE = typing.Union["ApplicationCommand", typing.Awaitable["ApplicationCommand"]]
    RESPONSE_AS_LIST = typing.Union[typing.List["ApplicationCommand"], typing.Awaitable[typing.List["ApplicationCommand"]]]

    def __init__(self,
                 name: str,
                 description: str,
                 command_type: typing.Union[int, "ApplicationCommandTypes"] = 1,
                 options: typing.List["ApplicationCommandOption"] = None,
                 default_permission: bool = True,
                 **resp):
        self.id = Snowflake.optional(resp.get("id"))
        self.type = ApplicationCommandTypes(int(command_type))
        self.application_id = Snowflake.optional(resp.get("application_id"))
        self.name = name
        self.description = description
        self.options = options or []
        self.default_permission = default_permission
        self.__command_creation = not resp

    def __int__(self):
        if self.id:
            return int(self.id)

    def to_dict(self):
        resp = {"name": self.name, "description": self.description, "options": [x.to_dict() for x in self.options], "default_permission": self.default_permission, "type": int(self.type)}
        if self.__command_creation:
            return resp
        resp["id"] = str(self.id)
        resp["application_id"] = str(self.application_id)
        return resp

    @classmethod
    def create(cls, resp):
        resp["options"] = [ApplicationCommandOption.create(x) for x in resp.pop("options", [])]
        resp["command_type"] = resp.pop("type", 1)
        return cls(**resp)


class ApplicationCommandTypes(TypeBase):
    CHAT_INPUT = 1
    USER = 2
    MESSAGE = 3


class ApplicationCommandOption:
    def __init__(self,
                 option_type: typing.Union["ApplicationCommandOptionType", int],
                 name: str,
                 description: str,
                 required: bool = False,
                 choices: typing.List["ApplicationCommandOptionChoice"] = None,
                 options: typing.List["ApplicationCommandOption"] = None,
                 **kw):
        self.type = ApplicationCommandOptionType(int(option_type))
        self.name = name
        self.description = description
        self.required = required
        self.choices = choices or []
        self.options = options or []

    def to_dict(self):
        ret = {"type": int(self.type), "name": self.name, "description": self.description, "required": self.required,
               "choices": [x.to_dict() for x in self.choices], "options": [x.to_dict() for x in self.options]}
        if not ret["options"]:
            del ret["options"]
        if not ret["choices"]:
            del ret["choices"]
        return ret

    @classmethod
    def create(cls, resp):
        resp["choices"] = [ApplicationCommandOptionChoice.create(x) for x in resp.get("choices", [])]
        resp["options"] = [cls.create(x) for x in resp.get("options", [])]
        resp["option_type"] = resp.pop("type")
        return cls(**resp)


class ApplicationCommandOptionType(TypeBase):
    SUB_COMMAND = 1
    SUB_COMMAND_GROUP = 2
    STRING = 3
    INTEGER = 4
    BOOLEAN = 5
    USER = 6
    CHANNEL = 7
    ROLE = 8
    MENTIONABLE = 9
    NUMBER = 10


class ApplicationCommandOptionChoice:
    def __init__(self, name: str, value: typing.Union[str, int, float], **kw):
        self.name = name
        self.value = value

    def to_dict(self):
        return {"name": self.name, "value": self.value}

    @classmethod
    def create(cls, resp):
        return cls(**resp)


class GuildApplicationCommandPermissions:
    RESPONSE = typing.Union["GuildApplicationCommandPermissions", typing.Awaitable["GuildApplicationCommandPermissions"]]
    RESPONSE_AS_LIST = typing.Union[typing.List["GuildApplicationCommandPermissions"], typing.Awaitable[typing.List["GuildApplicationCommandPermissions"]]]

    def __init__(self, resp: dict):
        self.id = Snowflake(resp["id"])
        self.application_id = Snowflake(resp["application_id"])
        self.guild_id = Snowflake(resp["guild_id"])
        self.permissions = [ApplicationCommandPermissions.create(x) for x in resp["permissions"]]


class ApplicationCommandPermissions:
    def __init__(self,
                 target: typing.Union[int, Role, User],
                 permission_type: typing.Union[int, "ApplicationCommandPermissionType"],
                 permission: bool,
                 **kw):
        self.id = Snowflake.ensure_snowflake(int(target))
        self.type = ApplicationCommandPermissionType(int(permission_type))
        self.permission = permission

    def to_dict(self):
        return {"id": str(self.id), "type": int(self.type), "permission": self.permission}

    @classmethod
    def create(cls, resp):
        resp["target"] = resp.pop("id")
        resp["permission_type"] = resp.pop("type")
        return cls(**resp)


class ApplicationCommandPermissionType(TypeBase):
    ROLE = 1
    USER = 2


class ApplicationCommandInteractionDataOption:
    def __init__(self, resp):
        self.name = resp["name"]
        self.type = ApplicationCommandOptionType(resp["type"])
        self.value = resp.get("value")
        self.options = [ApplicationCommandInteractionDataOption(x) for x in resp.get("options", [])]
