import datetime
from .guild import Member
from .snowflake import Snowflake


class VoiceState:
    def __init__(self, client, resp):
        self.raw = resp
        self.client = client
        self.guild_id = Snowflake.optional(resp.get("guild_id"))
        self.channel_id = Snowflake.optional(resp["channel_id"])
        self.user_id = Snowflake(resp["user_id"])
        self.__member = resp.get("member")
        self.member = Member.create(client, self.__member, user=self.user, guild_id=self.guild_id) if self.__member else self.__member
        self.session_id = resp["session_id"]
        self.deaf = resp["deaf"]
        self.mute = resp["mute"]
        self.self_deaf = resp["self_deaf"]
        self.self_mute = resp["self_mute"]
        self.self_stream = resp.get("self_stream")
        self.self_video = resp["self_video"]
        self.suppress = resp["suppress"]
        self.__request_to_speak_timestamp = resp["request_to_speak_timestamp"]
        self.request_to_speak_timestamp = datetime.datetime.fromisoformat(self.__request_to_speak_timestamp) if self.__request_to_speak_timestamp else self.__request_to_speak_timestamp

    @property
    def guild(self):
        if self.client.has_cache:
            return self.client.get(self.guild_id)

    @property
    def channel(self):
        if self.client.has_cache:
            return self.client.get(self.channel_id)

    @property
    def user(self):
        if self.client.has_cache:
            return self.client.get(self.user_id)

    @classmethod
    def create(cls, *args, **kwargs):
        return cls(*args, **kwargs)
