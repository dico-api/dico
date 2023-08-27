import typing

from ...base.model import CopyableObject, TypeBase
from ..channel import ChannelTypes
from ..emoji import Emoji
from ..snowflake import Snowflake


class Component(CopyableObject):
    def __init__(self, component_type: typing.Union[int, "ComponentTypes"]):
        self.type: ComponentTypes = (
            ComponentTypes(component_type)
            if isinstance(component_type, int)
            else component_type
        )

    def to_dict(self) -> dict:
        return {"type": self.type.value}

    @staticmethod
    def auto_detect(resp):
        if resp["type"] == ComponentTypes.ACTION_ROW:
            return ActionRow.create(resp)
        elif resp["type"] == ComponentTypes.BUTTON:
            return Button.create(resp)
        elif resp["type"] in (
            ComponentTypes.STRING_SELECT,
            ComponentTypes.USER_SELECT,
            ComponentTypes.ROLE_SELECT,
            ComponentTypes.MENTIONABLE_SELECT,
            ComponentTypes.CHANNEL_SELECT,
        ):
            return SelectMenu.create(resp)
        elif resp["type"] == ComponentTypes.TEXT_INPUT:
            if "style" not in resp:
                return TextInputResponse(resp)
            else:
                return TextInput.create(resp)
        else:
            raise NotImplementedError


class ComponentTypes(TypeBase):
    ACTION_ROW = 1
    BUTTON = 2
    STRING_SELECT = 3
    TEXT_INPUT = 4
    USER_SELECT = 5
    ROLE_SELECT = 6
    MENTIONABLE_SELECT = 7
    CHANNEL_SELECT = 8


class ActionRow(Component):
    def __init__(self, *components: typing.Union[Component, dict]):
        super().__init__(ComponentTypes.ACTION_ROW)
        self.components: typing.List[Component] = [
            Component.auto_detect(x) if isinstance(x, dict) else x
            for x in components or []
        ]

    def to_dict(self) -> dict:
        return {
            "type": self.type.value,
            "components": [x.to_dict() for x in self.components],
        }

    @classmethod
    def create(cls, resp):
        return cls(*[Component.auto_detect(x) for x in resp["components"]])


class Button(Component):
    def __init__(
        self,
        *,
        style: typing.Union["ButtonStyles", int],
        label: typing.Optional[str] = None,
        emoji: typing.Optional[typing.Union[Emoji, dict, "PartialEmoji", str]] = None,
        custom_id: typing.Optional[str] = None,
        url: typing.Optional[str] = None,
        disabled: typing.Optional[bool] = False,
        **_
    ):  # Dummy.
        super().__init__(ComponentTypes.BUTTON)
        self.style: ButtonStyles = (
            ButtonStyles(style) if isinstance(style, int) else style
        )
        self.label: typing.Optional[str] = label
        self.emoji: typing.Optional[PartialEmoji] = (
            PartialEmoji(emoji)
            if isinstance(emoji, dict)
            else PartialEmoji.from_full_emoji(emoji)
            if isinstance(emoji, Emoji)
            else PartialEmoji.from_str(emoji)
            if isinstance(emoji, str)
            else emoji
        )
        self.custom_id: typing.Optional[str] = custom_id
        self.url: typing.Optional[str] = url
        self.disabled: bool = disabled

    def to_dict(self) -> dict:
        ret = {"type": self.type.value}
        if self.style is not None:
            ret["style"] = self.style.value
        if self.label is not None:
            ret["label"] = self.label
        if self.emoji is not None:
            ret["emoji"] = self.emoji.to_dict()
        if self.custom_id is not None:
            ret["custom_id"] = self.custom_id
        if self.url is not None:
            ret["url"] = self.url
        if self.disabled is not None:
            ret["disabled"] = self.disabled
        return ret

    @classmethod
    def create(cls, resp: dict):
        return cls(**resp)


class ButtonStyles(TypeBase):
    PRIMARY = 1
    SECONDARY = 2
    SUCCESS = 3
    DANGER = 4
    LINK = 5


class SelectMenu(Component):
    def __init__(
        self,
        *,
        custom_id: str,
        options: typing.List[typing.Union["SelectOption", dict]],
        component_type: typing.Union[
            int, "ComponentTypes"
        ] = ComponentTypes.STRING_SELECT,
        channel_types: typing.List[int] = None,
        placeholder: typing.Optional[str] = None,
        min_values: typing.Optional[int] = None,
        max_values: typing.Optional[int] = None,
        disabled: typing.Optional[bool] = None,
        **kwargs
    ):
        super().__init__(kwargs.get("type", component_type))
        self.custom_id: str = custom_id
        self.options: typing.List[SelectOption] = [
            SelectOption.create(x) if isinstance(x, dict) else x for x in options
        ]
        self.channel_types: typing.Optional[
            typing.List[ChannelTypes]
        ] = channel_types and [ChannelTypes(x) for x in channel_types]
        self.placeholder: typing.Optional[str] = placeholder
        self.min_values: typing.Optional[int] = min_values
        self.max_values: typing.Optional[int] = max_values
        self.disabled: typing.Optional[bool] = disabled

    def to_dict(self) -> dict:
        ret = {"type": self.type.value}
        if self.custom_id is not None:
            ret["custom_id"] = self.custom_id
        if self.options is not None:
            ret["options"] = [x.to_dict() for x in self.options]
        if self.channel_types is not None:
            ret["channel_types"] = [int(x) for x in self.channel_types]
        if self.placeholder is not None:
            ret["placeholder"] = self.placeholder
        if self.min_values is not None:
            ret["min_values"] = self.min_values
        if self.max_values is not None:
            ret["max_values"] = self.max_values
        if self.disabled is not None:
            ret["disabled"] = self.disabled
        return ret

    @classmethod
    def create(cls, resp: dict):
        return cls(**resp)


class SelectOption:
    def __init__(
        self,
        *,
        label: str,
        value: str,
        description: typing.Optional[str] = None,
        emoji: typing.Optional[typing.Union["PartialEmoji", Emoji, dict, str]] = None,
        default: typing.Optional[bool] = None
    ):
        self.label: str = label
        self.value: str = value
        self.description: typing.Optional[str] = description
        self.emoji: typing.Optional[PartialEmoji] = (
            PartialEmoji(emoji)
            if isinstance(emoji, dict)
            else PartialEmoji.from_full_emoji(emoji)
            if isinstance(emoji, Emoji)
            else PartialEmoji.from_str(emoji)
            if isinstance(emoji, str)
            else emoji
        )
        self.default: typing.Optional[bool] = default

    def to_dict(self) -> dict:
        ret = {"label": self.label, "value": self.value}
        if self.description is not None:
            ret["description"] = self.description
        if self.emoji is not None:
            ret["emoji"] = self.emoji.to_dict()
        if self.default is not None:
            ret["default"] = self.default
        return ret

    @classmethod
    def create(cls, resp: dict):
        return cls(**resp)


class TextInput(Component):
    def __init__(
        self,
        *,
        custom_id: str,
        style: typing.Union["TextInputStyles", int],
        label: str,
        min_length: typing.Optional[int] = None,
        max_length: typing.Optional[int] = None,
        required: typing.Optional[bool] = None,
        value: typing.Optional[str] = None,
        placeholder: typing.Optional[str] = None,
        **_
    ):
        super().__init__(ComponentTypes.TEXT_INPUT)
        self.custom_id: str = custom_id
        self.style: TextInputStyles = TextInputStyles(int(style))
        self.label: str = label
        self.min_length: typing.Optional[int] = min_length
        self.max_length: typing.Optional[int] = max_length
        self.required: typing.Optional[bool] = required
        self.value: typing.Optional[str] = value
        self.placeholder: typing.Optional[str] = placeholder

    def to_dict(self) -> dict:
        ret = {
            "type": self.type.value,
            "custom_id": self.custom_id,
            "style": int(self.style),
            "label": self.label,
        }
        if self.min_length is not None:
            ret["min_length"] = self.min_length
        if self.max_length is not None:
            ret["max_length"] = self.max_length
        if self.required is not None:
            ret["required"] = self.required
        if self.value is not None:
            ret["value"] = self.value
        if self.placeholder is not None:
            ret["placeholder"] = self.placeholder
        return ret

    @classmethod
    def create(cls, resp: dict):
        return cls(**resp)


class TextInputResponse:
    def __init__(self, resp: dict):
        self.value: str = resp["value"]
        self.type: ComponentTypes = ComponentTypes(resp["type"])
        self.custom_id: str = resp["custom_id"]

    def to_dict(self) -> dict:
        raise AttributeError("unable to dump response")


class TextInputStyles(TypeBase):
    SHORT = 1
    PARAGRAPH = 2


class PartialEmoji:
    def __init__(self, resp: dict):
        self.name: str = resp["name"]
        self.id: typing.Optional[Snowflake] = Snowflake.optional(resp.get("id"))
        self.animated: bool = resp.get("animated", False)

    def to_dict(self) -> dict:
        resp = {"name": self.name}
        if self.id:
            resp["id"] = str(self.id)
            resp["animated"] = self.animated
        return resp

    @classmethod
    def from_full_emoji(cls, emoji: Emoji):
        return cls(
            {"name": emoji.name, "id": str(int(emoji.id)), "animated": emoji.animated}
        )

    @classmethod
    def from_str(cls, emoji: str):
        if not emoji.startswith("<") and not emoji.endswith(">"):
            return cls({"name": emoji, "id": None})
        emoji = emoji.lstrip("<").rstrip(">")
        animated = emoji.startswith("a:")
        name, emoji_id = emoji.lstrip("a:").split(":")
        return cls({"name": name, "id": emoji_id, "animated": animated})
