import typing
from .user import User
from .snowflake import Snowflake

if typing.TYPE_CHECKING:
    from .permission import Role


class Emoji:
    TYPING = typing.Union[int, str, Snowflake, "Emoji"]
    RESPONSE = typing.Union["Emoji", typing.Awaitable["Emoji"]]
    RESPONSE_AS_LIST = typing.Union[typing.List["Emoji"], typing.Awaitable[typing.List["Emoji"]]]

    def __init__(self, client, resp):
        self.id: typing.Optional[Snowflake] = Snowflake.optional(resp.get("id"))
        self.name: str = resp["name"]
        self.roles: typing.Optional[typing.List["Role"]] = [client.get(x) for x in resp.get("roles", [])] if client.has_cache else [Snowflake.optional(x) for x in resp.get("roles", [])]
        self.__user = resp.get("user")
        self.user: typing.Optional[User] = User.create(client, self.__user) if self.__user else self.__user
        self.require_colons: typing.Optional[bool] = resp.get("require_colons")
        self.managed: typing.Optional[bool] = resp.get("managed")
        self.animated: typing.Optional[bool] = resp.get("animated")
        self.available: typing.Optional[bool] = resp.get("available")

    def __str__(self):
        return f"<:{self.name}:{self.id}>" if self.id else self.name

    def __int__(self):
        return int(self.id)
