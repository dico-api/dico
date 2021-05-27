from ..emoji import Emoji
from ...base.model import TypeBase


class Component:
    def __init__(self, client, resp):
        self.type = ComponentTypes(resp["type"])
        self.style = ButtonStyles(resp["style"]) if resp.get("style") else None
        self.label = resp.get("label")
        self.__emoji = resp.get("emoji")
        self.emoji = Emoji(client, self.__emoji) if self.__emoji else self.__emoji
        self.custom_id = resp.get("custom_id")
        self.url = resp.get("url")
        self.disabled = resp.get("disabled", False)


class ComponentTypes(TypeBase):
    ACTION_ROW = 1
    BUTTON = 2


class Button(Component):
    pass


class ButtonStyles(TypeBase):
    PRIMARY = 1
    SECONDARY = 2
    SUCCESS = 3
    DANGER = 4
    LINK = 5
