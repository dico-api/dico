import typing

from ...base.model import TypeBase
from ..channel import ChannelTypes
from ..permission import Role
from ..snowflake import Snowflake
from ..user import User


class ApplicationCommand:
    TYPING = typing.Union[int, str, Snowflake, "ApplicationCommand"]
    RESPONSE = typing.Union[
        "ApplicationCommand", typing.Awaitable["ApplicationCommand"]
    ]
    RESPONSE_AS_LIST = typing.Union[
        typing.List["ApplicationCommand"],
        typing.Awaitable[typing.List["ApplicationCommand"]],
    ]

    def __init__(
        self,
        name: str,
        description: str,
        command_type: typing.Optional[typing.Union[int, "ApplicationCommandTypes"]] = 1,
        options: typing.Optional[typing.List["ApplicationCommandOption"]] = None,
        default_permission: typing.Optional[bool] = True,
        **resp
    ):
        self.id: typing.Optional[Snowflake] = Snowflake.optional(resp.get("id"))
        self.type: ApplicationCommandTypes = ApplicationCommandTypes(int(command_type))
        self.application_id: typing.Optional[Snowflake] = Snowflake.optional(
            resp.get("application_id")
        )
        self.name: str = name
        self.description: str = description
        self.options: typing.List[ApplicationCommandOption] = options or []
        self.default_permission: bool = default_permission
        self.__command_creation = not resp

    def __int__(self) -> int:
        if self.id:
            return int(self.id)

    def to_dict(self) -> dict:
        resp = {
            "name": self.name,
            "description": self.description,
            "options": [x.to_dict() for x in self.options],
            "default_permission": self.default_permission,
            "type": int(self.type),
        }
        if self.__command_creation:
            return resp
        resp["id"] = str(self.id)
        resp["application_id"] = str(self.application_id)
        return resp

    @classmethod
    def create(cls, resp):
        resp["options"] = [
            ApplicationCommandOption.create(x) for x in resp.pop("options", [])
        ]
        resp["command_type"] = resp.pop("type", 1)
        return cls(**resp)


class ApplicationCommandTypes(TypeBase):
    CHAT_INPUT = 1
    USER = 2
    MESSAGE = 3


class ApplicationCommandOption:
    def __init__(
        self,
        option_type: typing.Union["ApplicationCommandOptionType", int],
        name: str,
        description: str,
        required: typing.Optional[bool] = None,
        choices: typing.Optional[typing.List["ApplicationCommandOptionChoice"]] = None,
        autocomplete: typing.Optional[bool] = None,
        options: typing.Optional[typing.List["ApplicationCommandOption"]] = None,
        channel_types: typing.Optional[
            typing.List[typing.Union[int, ChannelTypes]]
        ] = None,
        **kw
    ):
        self.type: ApplicationCommandOptionType = ApplicationCommandOptionType(
            int(option_type)
        )
        self.name: str = name
        self.description: str = description
        self.required: typing.Optional[bool] = required
        self.choices: typing.Optional[
            typing.List[ApplicationCommandOptionChoice]
        ] = choices
        self.autocomplete: typing.Optional[bool] = autocomplete
        self.options: typing.Optional[typing.List[ApplicationCommandOption]] = options
        self.channel_types: typing.Optional[typing.List[ChannelTypes]] = (
            [*map(lambda x: ChannelTypes(int(x)), channel_types)]
            if channel_types is not None
            else channel_types
        )

    def to_dict(self) -> dict:
        ret = {
            "type": int(self.type),
            "name": self.name,
            "description": self.description,
        }
        if self.required is not None:
            ret["required"] = self.required
        if self.options is not None:
            ret["options"] = [x.to_dict() for x in self.options]
        if self.autocomplete is not None:
            ret["autocomplete"] = self.autocomplete
        if self.choices is not None:
            ret["choices"] = [x.to_dict() for x in self.choices]
        if self.channel_types is not None:
            ret["channel_types"] = [*map(int, self.channel_types)]
        return ret

    @classmethod
    def create(cls, resp):
        resp["choices"] = [
            ApplicationCommandOptionChoice.create(x) for x in resp.get("choices", [])
        ] or None
        resp["options"] = [cls.create(x) for x in resp.get("options", [])] or None
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
    ATTACHMENT = 11


class ApplicationCommandOptionChoice:
    def __init__(self, name: str, value: typing.Union[str, int, float], **kw):
        self.name: str = name
        self.value: typing.Union[str, int, float] = value

    def to_dict(self) -> dict:
        return {"name": self.name, "value": self.value}

    @classmethod
    def create(cls, resp):
        return cls(**resp)


class GuildApplicationCommandPermissions:
    RESPONSE = typing.Union[
        "GuildApplicationCommandPermissions",
        typing.Awaitable["GuildApplicationCommandPermissions"],
    ]
    RESPONSE_AS_LIST = typing.Union[
        typing.List["GuildApplicationCommandPermissions"],
        typing.Awaitable[typing.List["GuildApplicationCommandPermissions"]],
    ]

    def __init__(self, resp: dict):
        self.id: Snowflake = Snowflake(resp["id"])
        self.application_id: Snowflake = Snowflake(resp["application_id"])
        self.guild_id: Snowflake = Snowflake(resp["guild_id"])
        self.permissions: typing.List[ApplicationCommandPermissions] = [
            ApplicationCommandPermissions.create(x) for x in resp["permissions"]
        ]


class ApplicationCommandPermissions:
    def __init__(
        self,
        target: typing.Union[Role.TYPING, User.TYPING],
        permission_type: typing.Union[int, "ApplicationCommandPermissionType"],
        permission: bool,
        **kw
    ):
        self.id: typing.Optional[Snowflake] = Snowflake.ensure_snowflake(int(target))
        self.type: ApplicationCommandPermissionType = ApplicationCommandPermissionType(
            int(permission_type)
        )
        self.permission: bool = permission

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "type": int(self.type),
            "permission": self.permission,
        }

    @classmethod
    def create(cls, resp):
        resp["target"] = resp.pop("id")
        resp["permission_type"] = resp.pop("type")
        return cls(**resp)


class ApplicationCommandPermissionType(TypeBase):
    ROLE = 1
    USER = 2


class ApplicationCommandInteractionDataOption:
    def __init__(self, resp: dict):
        self.name: str = resp["name"]
        self.type: ApplicationCommandOptionType = ApplicationCommandOptionType(
            resp["type"]
        )
        self.value: typing.Optional = resp.get("value")
        self.options: typing.List[ApplicationCommandInteractionDataOption] = [
            ApplicationCommandInteractionDataOption(x) for x in resp.get("options", [])
        ]
        self.focused: typing.Optional[bool] = resp.get("focused")
