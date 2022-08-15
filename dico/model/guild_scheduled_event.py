import datetime
from typing import TYPE_CHECKING, Awaitable, List, Optional, Union

from ..base.model import DiscordObjectBase, TypeBase
from ..utils import cdn_url
from .snowflake import Snowflake
from .user import User

if TYPE_CHECKING:
    from ..api import APIClient


class GuildScheduledEvent(DiscordObjectBase):
    TYPING = Union[int, str, Snowflake, "GuildScheduledEvent"]
    RESPONSE = Union["GuildScheduledEvent", Awaitable["GuildScheduledEvent"]]
    RESPONSE_AS_LIST = Union[
        List["GuildScheduledEvent"], Awaitable[List["GuildScheduledEvent"]]
    ]
    _cache_type = "guild_scheduled_event"

    def __init__(self, client: "APIClient", resp: dict):
        super().__init__(client, resp)
        self.guild_id: Snowflake = Snowflake(resp["guild_id"])
        self.channel_id: Optional[Snowflake] = Snowflake.optional(resp["channel_id"])
        self.creator_id: Optional[Snowflake] = Snowflake.optional(
            resp.get("creator_id")
        )
        self.name: str = resp["name"]
        self.description: Optional[str] = resp.get("description")
        self.scheduled_start_time: datetime.datetime = datetime.datetime.fromisoformat(
            resp["scheduled_start_time"]
        )
        self.__scheduled_end_time = resp["scheduled_end_time"]
        self.scheduled_end_time: Optional[datetime.datetime] = (
            datetime.datetime.fromisoformat(self.__scheduled_end_time)
            if self.__scheduled_end_time
            else self.__scheduled_end_time
        )
        self.privacy_level: "GuildScheduledEventPrivacyLevel" = (
            GuildScheduledEventPrivacyLevel(resp["privacy_level"])
        )
        self.status: "GuildScheduledEventStatus" = GuildScheduledEventStatus(
            resp["status"]
        )
        self.entity_type: "GuildScheduledEventEntityTypes" = (
            GuildScheduledEventEntityTypes(resp["entity_type"])
        )
        self.entity_id: Optional[Snowflake] = Snowflake.optional(resp["entity_id"])
        self.entity_metadata: Optional[
            "GuildScheduledEventEntityMetadata"
        ] = GuildScheduledEventEntityMetadata.optional(resp.get("entity_metadata"))
        self.creator: Optional[User] = (
            User.create(client, resp["creator"]) if "creator" in resp else None
        )
        self.user_count: Optional[int] = resp.get("user_count")
        self.image: Optional[str] = resp.get("image")

    @property
    def link(self) -> str:
        return f"https://discord.com/events/{self.guild_id}/{self.id}"

    def __repr__(self):
        return f"<GuildScheduledEvent id={self.id} name={self.name}>"

    def image_url(self, *, extension: str = "webp", size: int = 1024) -> Optional[str]:
        if self.image:
            return cdn_url(
                "guild-events/{scheduled_event_id}",
                image_hash=self.image,
                extension=extension,
                size=size,
                scheduled_event_id=self.id,
            )


class GuildScheduledEventPrivacyLevel(TypeBase):
    GUILD_ONLY = 2


class GuildScheduledEventEntityTypes(TypeBase):
    STAGE_INSTANCE = 1
    VOICE = 2
    EXTERNAL = 3


class GuildScheduledEventStatus(TypeBase):
    SCHEDULED = 1
    ACTIVE = 2
    COMPLETED = 3
    CANCELED = 4


class GuildScheduledEventEntityMetadata:
    def __init__(self, *, location: Optional[str] = None):
        self.location = location

    def to_dict(self) -> dict:
        return {"location": self.location}

    @classmethod
    def optional(cls, resp: Optional[dict]):
        if resp:
            location = resp.get("location")
            return cls(location=location)


class GuildScheduledEventUser:
    RESPONSE_AS_LIST = Union[
        List["GuildScheduledEventUser"], Awaitable[List["GuildScheduledEventUser"]]
    ]

    def __init__(self, client: "APIClient", resp: dict):
        from .guild import GuildMember

        self.client: "APIClient" = client
        self.raw: dict = resp
        self.guild_scheduled_event_id: Snowflake = Snowflake(
            resp["guild_scheduled_event_id"]
        )
        self.user: User = User.create(client, resp["user"])
        self.member: Optional[GuildMember] = (
            GuildMember.create(client, resp["member"]) if "member" in resp else None
        )
