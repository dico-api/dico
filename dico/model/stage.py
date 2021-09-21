import typing

from .snowflake import Snowflake
from ..base.model import DiscordObjectBase, TypeBase

if typing.TYPE_CHECKING:
    from .channel import Channel
    from .guild import Guild
    from ..api import APIClient


class StageInstance(DiscordObjectBase):
    TYPING = typing.Union[int, str, Snowflake, "StageInstance"]
    RESPONSE = typing.Union["StageInstance", typing.Awaitable["StageInstance"]]
    RESPONSE_AS_LIST = typing.Union[typing.List["StageInstance"], typing.Awaitable[typing.List["StageInstance"]]]
    _cache_type = "stage_instance"

    def __init__(self, client: "APIClient", resp: dict):
        super().__init__(client, resp)
        self.guild_id: Snowflake = Snowflake(resp["guild_id"])
        self.channel_id: Snowflake = Snowflake(resp["channel_id"])
        self.topic: str = resp["topic"]
        self.privacy_level: PrivacyLevel = PrivacyLevel(resp["privacy_level"])
        self.discoverable_disabled: bool = resp["discoverable_disabled"]

    @property
    def guild(self) -> typing.Optional["Guild"]:
        if self.client.has_cache:
            return self.client.get(self.guild_id, "guild")

    @property
    def channel(self) -> typing.Optional["Channel"]:
        if self.client.has_cache:
            return self.client.get(self.channel_id, "channel")

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}>"


class PrivacyLevel(TypeBase):
    PUBLIC = 1
    GUILD_ONLY = 2
