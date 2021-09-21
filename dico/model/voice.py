import typing
import datetime
from .guild import GuildMember, Guild
from .snowflake import Snowflake

if typing.TYPE_CHECKING:
    from .channel import Channel
    from .user import User
    from ..api import APIClient


class VoiceState:
    def __init__(self, client: "APIClient", resp: dict):
        self.raw: dict = resp
        self.client: "APIClient" = client
        self.guild_id: typing.Optional[Snowflake] = Snowflake.optional(resp.get("guild_id"))
        self.channel_id: typing.Optional[Snowflake] = Snowflake.optional(resp["channel_id"])
        self.user_id: Snowflake = Snowflake(resp["user_id"])
        self.__member = resp.get("member")
        self.member: typing.Optional[GuildMember] = GuildMember.create(client, self.__member, user=self.user, guild_id=self.guild_id) if self.__member else self.__member
        self.session_id: str = resp["session_id"]
        self.deaf: bool = resp["deaf"]
        self.mute: bool = resp["mute"]
        self.self_deaf: bool = resp["self_deaf"]
        self.self_mute: bool = resp["self_mute"]
        self.self_stream: bool = resp.get("self_stream")
        self.self_video: bool = resp["self_video"]
        self.suppress: bool = resp["suppress"]
        self.__request_to_speak_timestamp = resp["request_to_speak_timestamp"]
        self.request_to_speak_timestamp: typing.Optional[datetime.datetime] = datetime.datetime.fromisoformat(self.__request_to_speak_timestamp) \
            if self.__request_to_speak_timestamp else self.__request_to_speak_timestamp

    @property
    def guild(self) -> typing.Optional[Guild]:
        if self.client.has_cache:
            return self.client.get(self.guild_id, "guild")

    @property
    def channel(self) -> "Channel":
        if self.client.has_cache:
            return self.client.get(self.channel_id, "channel")

    @property
    def user(self) -> "User":
        if self.client.has_cache:
            return self.client.get(self.user_id, "user")

    @classmethod
    def create(cls, *args, **kwargs):
        return cls(*args, **kwargs)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"

class VoiceRegion:
    RESPONSE = typing.Union["VoiceRegion", typing.Awaitable["VoiceRegion"]]
    RESPONSE_AS_LIST = typing.Union[typing.List["VoiceRegion"], typing.Awaitable[typing.List["VoiceRegion"]]]

    def __init__(self, resp: dict):
        self.id: str = resp["id"]
        self.name: str = resp["name"]
        self.vip: bool = resp.get("vip")
        self.optimal: bool = resp["optimal"]
        self.deprecated: bool = resp["deprecated"]
        self.custom: bool = resp["custom"]
         
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id} name={self.name}>"
          

class VoiceOpcodes:
    IDENTIFY = 0
    SELECT_PROTOCOL = 1
    READY = 2
    HEARTBEAT = 3
    SESSION_DESCRIPTION = 4
    SPEAKING = 5
    HEARTBEAT_ACK = 6
    RESUME = 7
    HELLO = 8
    RESUMED = 9
    CLIENT_DISCONNECT = 13

    @staticmethod
    def as_string(code: int) -> str:
        opcodes = {0: "Identify",
                   1: "Select Protocol",
                   2: "Ready",
                   3: "Heartbeat",
                   4: "Session Description",
                   5: "Speaking",
                   6: "Heartbeat ACK",
                   7: "Resume",
                   8: "Hello",
                   9: "Resumed",
                   13: "Client Disconnect"}
        return opcodes.get(code)
