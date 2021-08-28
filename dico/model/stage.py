from .snowflake import Snowflake
from ..base.model import DiscordObjectBase, TypeBase


class StageInstance(DiscordObjectBase):
    def __init__(self, client, resp):
        super().__init__(client, resp)
        self._cache_type = "stage_instance"
        self.guild_id = Snowflake(resp["guild_id"])
        self.channel_id = Snowflake(resp["channel_id"])
        self.topic = resp["topic"]
        self.privacy_level = PrivacyLevel(resp["privacy_level"])
        self.discoverable_disabled = resp["discoverable_disabled"]

    @property
    def guild(self):
        if self.client.has_cache:
            return self.client.get(self.guild_id, "guild")

    @property
    def channel(self):
        if self.client.has_cache:
            return self.client.get(self.channel_id, "channel")


class PrivacyLevel(TypeBase):
    PUBLIC = 1
    GUILD_ONLY = 2
