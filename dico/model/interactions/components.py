import typing

from ..emoji import Emoji
from ..snowflake import Snowflake
from ...base.model import TypeBase


class Component:
    def __init__(self, component_type: typing.Union[int, "ComponentTypes"]):
        self.type = ComponentTypes(component_type) if isinstance(component_type, int) else component_type

    def to_dict(self):
        return {"type": self.type.value}

    @staticmethod
    def auto_detect(resp):
        if resp["type"] == ComponentTypes.ACTION_ROW:
            return ActionRow.create(resp)
        elif resp["type"] == ComponentTypes.BUTTON:
            return Button.create(resp)
        elif resp["type"] == ComponentTypes.SELECT_MENU:
            return SelectMenu.create(resp)
        else:
            raise NotImplementedError


class ComponentTypes(TypeBase):
    ACTION_ROW = 1
    BUTTON = 2
    SELECT_MENU = 3


class ActionRow(Component):
    def __init__(self, *components: typing.Union[Component, dict]):
        super().__init__(ComponentTypes.ACTION_ROW)
        self.components = [Component.auto_detect(x) if isinstance(x, dict) else x for x in components or []]

    def to_dict(self):
        return {"type": self.type.value, "components": [x.to_dict() for x in self.components]}

    @classmethod
    def create(cls, resp):
        return cls(*[Component.auto_detect(x) for x in resp["components"]])


class Button(Component):
    def __init__(self,
                 *,
                 style: typing.Union["ButtonStyles", int],
                 label: str = None,
                 emoji: typing.Union[Emoji, dict, "PartialEmoji"] = None,
                 custom_id: str = None,
                 url: str = None,
                 disabled: bool = False,
                 **_):  # Dummy.
        super().__init__(ComponentTypes.BUTTON)
        self.style = ButtonStyles(style) if isinstance(style, int) else style
        self.label = label
        self.emoji = PartialEmoji(emoji) if isinstance(emoji, dict) else PartialEmoji.from_full_emoji(emoji) if isinstance(emoji, Emoji) else emoji
        self.custom_id = custom_id
        self.url = url
        self.disabled = disabled

    def to_dict(self):
        ret = {"type": self.type.value}
        if self.style is not None:
            ret["style"] = self.style.value
        if self.label is not None:
            ret["label"] = self.label
        if self.emoji is not None:
            ret["emoji"] = {"name": self.emoji.name, "id": self.emoji.id, "animated": self.emoji.animated or False}  # We only need name, id, and animated
        if self.custom_id is not None:
            ret["custom_id"] = self.custom_id
        if self.url is not None:
            ret["url"] = self.url
        if self.disabled is not None:
            ret["disabled"] = self.disabled
        return ret

    @classmethod
    def create(cls, resp):
        return cls(**resp)


class ButtonStyles(TypeBase):
    PRIMARY = 1
    SECONDARY = 2
    SUCCESS = 3
    DANGER = 4
    LINK = 5


class SelectMenu(Component):
    def __init__(self,
                 *,
                 custom_id: str,
                 options: typing.List[typing.Union["SelectOptions", dict]],
                 placeholder: str = None,
                 min_values: int = None,
                 max_values: int = None,
                 **_):  # Dummy.
        super().__init__(ComponentTypes.SELECT_MENU)
        self.custom_id = custom_id
        self.options = [SelectOptions.create(x) if isinstance(x, dict) else x for x in options]
        self.placeholder = placeholder
        self.min_values = min_values
        self.max_values = max_values

    def to_dict(self):
        ret = {"type": self.type.value}
        if self.custom_id is not None:
            ret["custom_id"] = self.custom_id
        if self.options is not None:
            ret["options"] = [x.to_dict() for x in self.options]
        if self.placeholder is not None:
            ret["placeholder"] = self.placeholder
        if self.min_values is not None:
            ret["min_values"] = self.min_values
        if self.max_values is not None:
            ret["max_values"] = self.max_values
        return ret

    @classmethod
    def create(cls, resp):
        return cls(**resp)


class SelectOptions:
    def __init__(self,
                 *,
                 label: str,
                 value: str,
                 description: str = None,
                 emoji: typing.Union["PartialEmoji", Emoji, dict] = None,
                 default: bool = None):
        self.label = label
        self.value = value
        self.description = description
        self.emoji = PartialEmoji(emoji) if isinstance(emoji, dict) else PartialEmoji.from_full_emoji(emoji) if isinstance(emoji, Emoji) else emoji
        self.default = default

    def to_dict(self):
        ret = {"label": self.label, "value": self.value}
        if self.description is not None:
            ret["description"] = self.description
        if self.emoji is not None:
            ret["emoji"] = {"name": self.emoji.name, "id": self.emoji.id, "animated": self.emoji.animated or False}  # We only need name, id, and animated
        if self.default is not None:
            ret["default"] = self.default
        return ret

    @classmethod
    def create(cls, resp):
        return cls(**resp)


class PartialEmoji:
    def __init__(self, resp):
        self.name = resp["name"]
        self.id = Snowflake.optional(resp.get("id"))
        self.animated = resp.get("animated")

    @classmethod
    def from_full_emoji(cls, emoji: Emoji):
        return cls({"name": emoji.name, "id": int(emoji.id), "animated": emoji.animated})
