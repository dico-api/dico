import typing
from .channel import Channel, Message
from .guild import Guild
from .snowflake import Snowflake
from .user import User
from ..base.model import TypeBase


class Webhook:
    TYPING = typing.Union[int, str, Snowflake, "Webhook"]
    RESPONSE = typing.Union["Webhook", typing.Awaitable["Webhook"]]
    RESPONSE_AS_LIST = typing.Union[typing.List["Webhook"], typing.Awaitable[typing.List["Webhook"]]]

    def __init__(self, client, resp):
        self.raw = resp
        self.client = client
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

    def __int__(self):
        return int(self.id)

    def modify(self, **kwargs):
        new_wh = self.client.modify_webhook(self, **kwargs)
        if not isinstance(new_wh, Webhook):
            return self.__async_modify(new_wh)
        return self.__modify(new_wh)

    async def __async_modify(self, new_wh):
        new_wh = await new_wh
        return self.__modify(new_wh)

    def __modify(self, new_wh):
        for k, v in new_wh.raw.items():
            if self.raw[k] != v:
                self.raw[k] = v
        self.__init__(self.client, self.raw)
        return self

    def delete(self):
        return self.client.delete_webhook(self)

    def execute(self, **kwargs):
        return self.client.execute_webhook(self, **kwargs)

    def request_message(self, message: typing.Union[str, int, Snowflake, Message]):
        return self.client.request_webhook_message(self, message)

    @property
    def edit(self):
        return self.modify

    @property
    def send(self):
        return self.execute


class WebhookTypes(TypeBase):
    INCOMING = 1
    CHANNEL_FOLLOWER = 2
