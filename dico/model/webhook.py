from .channel import Channel
from .guild import Guild
from .snowflake import Snowflake
from .user import User
from ..base.model import TypeBase


class Webhook:
    def __init__(self, client, resp):
        self.id = Snowflake(resp["id"])
        self.type = WebhookTypes(resp["type"])
        self.guild_id = Snowflake.optional(resp.get("guild_id"))
        self.channel_id = Snowflake(resp["channel_id"])
        self.__user = resp["user"]
        self.user = User.create(client, self.__user) if self.__user else self.__user
        self.name = resp["name"]
        self.avatar = resp["avatar"]
        self.token = resp.get("token")
        self.application_id = Snowflake.optional(resp["application_id"])
        self.__source_guild = resp.get("source_guild")
        self.source_guild = Guild.create(client, self.__source_guild) if self.__source_guild else self.__source_guild
        self.__source_channel = resp.get("source_channel")
        self.source_channel = Channel.create(client, self.__source_channel) if self.__source_channel else self.__source_channel
        self.url = resp.get("url")


class WebhookTypes(TypeBase):
    INCOMING = 1
    CHANNEL_FOLLOWER = 2
