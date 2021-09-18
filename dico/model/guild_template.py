import typing
import datetime
from .guild import Guild
from .snowflake import Snowflake
from .user import User

if typing.TYPE_CHECKING:
    from ..api import APIClient


class GuildTemplate:
    TYPING = typing.Union[str, "GuildTemplate"]
    RESPONSE = typing.Union["GuildTemplate", typing.Awaitable["GuildTemplate"]]
    RESPONSE_AS_LIST = typing.Union[typing.List["GuildTemplate"], typing.Awaitable[typing.List["GuildTemplate"]]]

    def __init__(self, client: "APIClient", resp: dict):
        self.raw: dict = resp
        self.client: "APIClient" = client
        self.code: str = resp["code"]
        self.name: str = resp["name"]
        self.description: typing.Optional[str] = resp["description"]
        self.usage_count: int = resp["usage_count"]
        self.creator_id: Snowflake = Snowflake(resp["creator_id"])
        self.creator: User = User.create(client, resp["creator"])
        self.created_at: datetime.datetime = datetime.datetime.fromisoformat(resp["created_at"])
        self.updated_at: datetime.datetime = datetime.datetime.fromisoformat(resp["updated_at"])
        self.source_guild_id: Snowflake = Snowflake(resp["source_guild_id"])
        self.serialized_source_guild: Guild = Guild.create(client, resp["serialized_source_guild"])
        self.is_dirty: typing.Optional[bool] = resp["is_dirty"]

    def __str__(self) -> str:
        return self.code
