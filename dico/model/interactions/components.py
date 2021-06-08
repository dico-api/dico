import typing

from ..emoji import Emoji
from ...base.model import TypeBase


class Component:
    def __init__(self, client, resp):
        self.client = client
        self.type = ComponentTypes(resp["type"])

    def to_dict(self):
        return {"type": self.type.value}

    @classmethod
    def auto_detect(cls, client, resp):
        if resp["type"] == ComponentTypes.ACTION_ROW:
            return ActionRow(client, resp)
        elif resp["type"] == ComponentTypes.BUTTON:
            return Button(client, resp)


class ComponentTypes(TypeBase):
    ACTION_ROW = 1
    BUTTON = 2


class ActionRow(Component):
    def __init__(self, client, resp):
        super().__init__(client, resp)
        self.components = [Component.auto_detect(client, x) for x in resp.get("components", [])]

    def to_dict(self):
        return {"type": self.type.value, "components": [x.to_dict() for x in self.components]}

    @classmethod
    def create(cls, client, components: typing.List[typing.Union[Component, dict]]):
        return cls(client, {"type": 1, "components": [x.to_dict() if not isinstance(x, dict) else x for x in components]})


class Button(Component):
    def __init__(self, client, resp):
        super().__init__(client, resp)
        self.style = ButtonStyles(resp["style"]) if resp.get("style") else None
        self.label = resp.get("label")
        self.__emoji = resp.get("emoji")
        self.emoji = Emoji(client, self.__emoji) if self.__emoji else self.__emoji
        self.custom_id = resp.get("custom_id")
        self.url = resp.get("url")
        self.disabled = resp.get("disabled", False)

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
    def create(cls,
               client,
               *,
               style: typing.Union["ButtonStyles", int],
               label: str = None,
               emoji: typing.Union[Emoji, dict] = None,
               custom_id: str = None,
               url: str = None,
               disabled: bool = False):
        return cls(client,
                   {"type": 2,
                    "style": int(style),
                    "label": label,
                    "emoji": emoji if isinstance(emoji, dict) or emoji is None else {"name": emoji.name, "id": emoji.id, "animated": emoji.animated or False},
                    "custom_id": custom_id,
                    "url": url,
                    "disabled": disabled})


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
