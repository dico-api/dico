from ..model.snowflake import Snowflake


class EventBase:
    def __init__(self, client, resp: dict):
        self.raw = resp

    @classmethod
    def create(cls, client, resp: dict):
        return cls(client, resp)


class DiscordObjectBase:
    def __init__(self, client, resp):
        self.id = Snowflake(resp["id"])
        self.client = client

    def __int__(self):
        return int(self.id)
