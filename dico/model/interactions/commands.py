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
        name_localizations: typing.Optional[typing.Dict[str, str]] = None,
        description_localizations: typing.Optional[typing.Dict[str, str]] = None,
        command_type: typing.Optional[typing.Union[int, "ApplicationCommandTypes"]] = 1,
        options: typing.Optional[typing.List["ApplicationCommandOption"]] = None,
        default_member_permissions: typing.Optional[str] = None,
        dm_permission: typing.Optional[bool] = None,
        default_permission: typing.Optional[bool] = True,
        nsfw: typing.Optional[bool] = None,
        **resp
    ):
        self.id: typing.Optional[Snowflake] = Snowflake.optional(resp.get("id"))
        self.type: ApplicationCommandTypes = ApplicationCommandTypes(int(command_type))
        self.application_id: typing.Optional[Snowflake] = Snowflake.optional(
            resp.get("application_id")
        )
        self.guild_id: typing.Optional[Snowflake] = Snowflake.optional(
            resp.get("guild_id")
        )
        self.name: str = name
        self.name_localizations: typing.Optional[
            typing.Dict[str, str]
        ] = name_localizations
        self.description: str = description
        self.description_localizations: typing.Optional[
            typing.Dict[str, str]
        ] = description_localizations
        self.options: typing.List[ApplicationCommandOption] = options or []
        self.default_member_permissions = default_member_permissions
        self.dm_permission = dm_permission
        self.default_permission: bool = default_permission
        self.nsfw: typing.Optional[bool] = nsfw
        self.version: Snowflake = Snowflake.optional(resp.get("version"))

        self.__command_creation = not resp

    def __int__(self) -> int:
        if self.id:
            return int(self.id)

    def to_dict(self) -> dict:
        resp = {
            "name": self.name,
            "description": self.description,
            "options": [x.to_dict() for x in self.options],
            "default_member_permissions": self.default_member_permissions,
            "dm_permission": self.dm_permission,
            "default_permission": self.default_permission,
            "type": int(self.type),
        }
        if self.nsfw is not None:
            resp["nsfw"] = self.nsfw
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
        name_localizations: typing.Optional[typing.Dict[str, str]] = None,
        description_localizations: typing.Optional[typing.Dict[str, str]] = None,
        required: typing.Optional[bool] = None,
        choices: typing.Optional[typing.List["ApplicationCommandOptionChoice"]] = None,
        autocomplete: typing.Optional[bool] = None,
        options: typing.Optional[typing.List["ApplicationCommandOption"]] = None,
        channel_types: typing.Optional[
            typing.List[typing.Union[int, ChannelTypes]]
        ] = None,
        min_value: typing.Optional[typing.Union[int, float]] = None,
        max_value: typing.Optional[typing.Union[int, float]] = None,
        min_length: typing.Optional[int] = None,
        max_length: typing.Optional[int] = None,
        **kw
    ):
        self.type: ApplicationCommandOptionType = ApplicationCommandOptionType(
            int(option_type)
        )
        self.name: str = name
        self.name_localizations: typing.Optional[
            typing.Dict[str, str]
        ] = name_localizations
        self.description: str = description
        self.description_localizations: typing.Optional[
            typing.Dict[str, str]
        ] = description_localizations
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
        self.min_value: typing.Optional[typing.Union[int, float]] = min_value
        self.max_value: typing.Optional[typing.Union[int, float]] = max_value
        self.min_length: typing.Optional[int] = min_length
        self.max_length: typing.Optional[int] = max_length

    def to_dict(self) -> dict:
        ret = {
            "type": int(self.type),
            "name": self.name,
            "description": self.description,
        }
        if self.name_localizations is not None:
            ret["name_localizations"] = self.name_localizations
        if self.description_localizations is not None:
            ret["description_localizations"] = self.description_localizations
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
        if self.min_value is not None:
            ret["min_value"] = self.min_value
        if self.max_value is not None:
            ret["max_value"] = self.max_value
        if self.min_length is not None:
            ret["min_length"] = self.min_length
        if self.max_length is not None:
            ret["max_length"] = self.max_length
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
    def __init__(
        self,
        name: str,
        value: typing.Union[str, int, float],
        name_localizations: typing.Optional[typing.Dict[str, str]] = None,
        **kw
    ):
        self.name: str = name
        self.name_localizations: typing.Optional[
            typing.Dict[str, str]
        ] = name_localizations
        self.value: typing.Union[str, int, float] = value

    def to_dict(self) -> dict:
        ret = {"name": self.name, "value": self.value}
        if self.name_localizations is not None:
            ret["name_localizations"] = self.name_localizations
        return ret

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
    CHANNEL = 3


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
