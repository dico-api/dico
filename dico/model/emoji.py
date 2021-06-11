from .user import User
from .snowflake import Snowflake


class Emoji:
    def __init__(self, client, resp):
        self.id = Snowflake.optional(resp.get("id"))
        self.name = resp["name"]
        self.roles = [client.get(x) for x in resp.get("roles", [])] if client.has_cache else [Snowflake.optional(x) for x in resp.get("roles", [])]
        self.__user = resp.get("user")
        self.user = User.create(client, self.__user) if self.__user else self.__user
        self.require_colons = resp.get("require_colons")
        self.managed = resp.get("managed")
        self.animated = resp.get("animated")
        self.available = resp.get("available")

    def __str__(self):
        return f"<:{self.name}:{self.id}>" if self.id else self.name

    def __int__(self):
        return int(self.id)
