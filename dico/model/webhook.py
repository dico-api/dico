import typing
from .channel import Channel, Message
from .guild import Guild
from .snowflake import Snowflake
from .user import User
from ..base.model import TypeBase

if typing.TYPE_CHECKING:
    from ..api import APIClient


class Webhook:
    TYPING = typing.Union[int, str, Snowflake, "Webhook"]
    RESPONSE = typing.Union["Webhook", typing.Awaitable["Webhook"]]
    RESPONSE_AS_LIST = typing.Union[typing.List["Webhook"], typing.Awaitable[typing.List["Webhook"]]]

    def __init__(self, client: "APIClient", resp: dict):
        self.raw: dict = resp
        self.client: "APIClient" = client
        self.id: Snowflake = Snowflake(resp["id"])
        self.type: WebhookTypes = WebhookTypes(resp["type"])
        self.guild_id: typing.Optional[Snowflake] = Snowflake.optional(resp.get("guild_id"))
        self.channel_id: Snowflake = Snowflake(resp["channel_id"])
        self.__user = resp["user"]
        self.user: typing.Optional[User] = User.create(client, self.__user) if self.__user else self.__user
        self.name: typing.Optional[str] = resp["name"]
        self.avatar: typing.Optional[str] = resp["avatar"]
        self.token: typing.Optional[str] = resp.get("token")
        self.application_id: typing.Optional[Snowflake] = Snowflake.optional(resp["application_id"])
        self.__source_guild = resp.get("source_guild")
        self.source_guild: typing.Optional[Guild] = Guild.create(client, self.__source_guild) if self.__source_guild else self.__source_guild
        self.__source_channel = resp.get("source_channel")
        self.source_channel: typing.Optional[Channel] = Channel.create(client, self.__source_channel) if self.__source_channel else self.__source_channel
        self.url: typing.Optional[str] = resp.get("url")

    def __int__(self) -> int:
        return int(self.id)

    def modify(self, **kwargs) -> "Webhook.RESPONSE":
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

    def execute(self, **kwargs) -> Message.RESPONSE:
        return self.client.execute_webhook(self, **kwargs)

    def request_message(self, message: typing.Union[str, int, Snowflake, Message]) -> Message.RESPONSE:
        return self.client.request_webhook_message(self, message)

    @property
    def edit(self):
        return self.modify

    @property
    def send(self):
        return self.execute

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id} name={self.name}>"


class WebhookTypes(TypeBase):
    INCOMING = 1
    CHANNEL_FOLLOWER = 2
