import typing

from ..emoji import Emoji
from ...base.model import TypeBase


class Component:
    def __init__(self, client, component_type: typing.Union[int, "ComponentTypes"]):
        self.client = client
        self.type = ComponentTypes(component_type) if isinstance(component_type, int) else component_type

    def to_dict(self):
        return {"type": self.type.value}

    @classmethod
    def auto_detect(cls, client, resp):
        if resp["type"] == ComponentTypes.ACTION_ROW:
            return ActionRow.create(client, resp)
        elif resp["type"] == ComponentTypes.BUTTON:
            return Button.create(client, resp)
        else:
            raise NotImplementedError


class ComponentTypes(TypeBase):
    ACTION_ROW = 1
    BUTTON = 2


class ActionRow(Component):
    def __init__(self, client, *components: typing.Union[Component, dict]):
        super().__init__(client, ComponentTypes.ACTION_ROW)
        self.components = [Component.auto_detect(client, x) if isinstance(x, dict) else x for x in components or []]

    def to_dict(self):
        return {"type": self.type.value, "components": [x.to_dict() for x in self.components]}

    @classmethod
    def create(cls, client, resp):
        return cls(client, *[Component.auto_detect(client, x) for x in resp["components"]])


class Button(Component):
    def __init__(self,
                 client,
                 *,
                 style: typing.Union["ButtonStyles", int],
                 label: str = None,
                 emoji: typing.Union[Emoji, dict] = None,
                 custom_id: str = None,
                 url: str = None,
                 disabled: bool = False,
                 **_):  # Dummy.
        super().__init__(client, ComponentTypes.BUTTON)
        self.style = ButtonStyles(style) if isinstance(style, int) else style
        self.label = label
        self.__emoji = emoji
        self.emoji = Emoji(client, self.__emoji) if isinstance(emoji, dict) else self.__emoji
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
    def create(cls, client, resp):
        return cls(client, **resp)


class ButtonStyles(TypeBase):
    PRIMARY = 1
    SECONDARY = 2
    SUCCESS = 3
    DANGER = 4
    LINK = 5


class TemporaryComponentResponse:
    def __init__(self, resp):
        self.raw = resp
        self.custom_id = resp.get("custom_id")
        self.component_type = ComponentTypes(resp.get("component_type")) if resp.get("component_type") else None
