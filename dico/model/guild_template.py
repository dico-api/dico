import typing
import datetime
from .guild import Guild
from .snowflake import Snowflake
from .user import User


class GuildTemplate:
    TYPING = typing.Union[str, "GuildTemplate"]
    RESPONSE = typing.Union["GuildTemplate", typing.Awaitable["GuildTemplate"]]
    RESPONSE_AS_LIST = typing.Union[typing.List["GuildTemplate"], typing.Awaitable[typing.List["GuildTemplate"]]]

    def __init__(self, client, resp):
        self.raw = resp
        self.client = client
        self.code = resp["code"]
        self.description = resp["description"]
        self.usage_count = resp["usage_count"]
        self.creator_id = Snowflake(resp["creator_id"])
        self.name = resp["name"]
        self.name = resp["name"]
        self.creator = User.create(client, resp["creator"])
        self.created_at = datetime.datetime.fromisoformat(resp["created_at"])
        self.updated_at = datetime.datetime.fromisoformat(resp["updated_at"])
        self.source_guild_id = Snowflake(resp["source_guild_id"])
        self.serialized_source_guild = Guild.create(client, resp["serialized_source_guild"])
        self.is_dirty = resp["is_dirty"]

    def __str__(self):
        return self.code
