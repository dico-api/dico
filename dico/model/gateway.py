import datetime
import typing

from ..base.model import FlagBase, TypeBase
from ..utils import cdn_url
from .snowflake import Snowflake


class GetGateway:
    def __init__(self, resp: dict):
        self.url: str = resp["url"]
        self.shards: typing.Optional[int] = resp.get("shards", 0)
        self.session_start_limit: typing.Optional[
            SessionStartLimit
        ] = SessionStartLimit.optional(resp.get("session_start_limit"))

    def to_dict(self) -> dict:
        return {
            "url": self.url,
            "shards": self.shards,
            "session_start_limit": self.session_start_limit,
        }


class SessionStartLimit:
    def __init__(self, resp: dict):
        self.total = resp["total"]
        self.remaining = resp["remaining"]
        self.reset_after = resp["reset_after"]
        self.max_concurrency = resp["max_concurrency"]

    @classmethod
    def optional(cls, resp: dict):
        if resp:
            return cls(resp)

    def to_dict(self):
        return {
            "total": self.total,
            "remaining": self.remaining,
            "reset_after": self.reset_after,
            "max_concurrency": self.max_concurrency,
        }


class Intents(FlagBase):
    GUILDS = 1 << 0
    GUILD_MEMBERS = 1 << 1
    GUILD_BANS = 1 << 2
    GUILD_EMOJIS = 1 << 3
    GUILD_INTEGRATIONS = 1 << 4
    GUILD_WEBHOOKS = 1 << 5
    GUILD_INVITES = 1 << 6
    GUILD_VOICE_STATES = 1 << 7
    GUILD_PRESENCES = 1 << 8
    GUILD_MESSAGES = 1 << 9
    GUILD_MESSAGE_REACTIONS = 1 << 10
    GUILD_MESSAGE_TYPING = 1 << 11
    DIRECT_MESSAGES = 1 << 12
    DIRECT_MESSAGE_REACTIONS = 1 << 13
    DIRECT_MESSAGE_TYPING = 1 << 14
    MESSAGE_CONTENT = 1 << 15
    GUILD_SCHEDULED_EVENTS = 1 << 16

    @classmethod
    def full(cls):
        return cls(*[x for x in dir(cls) if isinstance(getattr(cls, x), int)])

    @classmethod
    def no_privileged(cls):
        intents = cls.full()
        intents.guild_presences = False
        intents.guild_members = False
        intents.message_content = False
        return intents

    @classmethod
    def guild(cls):
        intents = cls.full()
        intents.direct_messages = False
        intents.direct_message_reactions = False
        intents.direct_message_typing = False
        return intents

    @classmethod
    def dm(cls):
        intents = cls.none()
        intents.direct_messages = True
        intents.direct_message_reactions = True
        intents.direct_message_typing = True
        return intents

    @classmethod
    def none(cls):
        return cls()


class GatewayResponse:
    def __init__(self, resp: dict):
        self.raw = resp
        self.op = resp["op"]
        self.d = resp.get("d", {})
        self.s = resp.get("s")
        self.t = resp.get("t")

    def to_dict(self):
        return {"op": self.op, "d": self.d, "s": self.s, "t": self.t}


class Activity:
    def __init__(self, resp=None, *, name=None, activity_type=None, url=None):
        if resp is None:
            if name is None or activity_type is None:
                raise ValueError("parameter name and activity_type is required.")
            resp = {"name": name, "type": activity_type, "url": url}
        self.name = resp["name"]
        self.type = ActivityTypes(resp["type"])
        self.url = resp.get("url")
        self.__created_at = resp.get("created_at")
        self.created_at = (
            datetime.datetime.fromtimestamp(self.__created_at / 1000)
            if self.__created_at
            else self.__created_at
        )
        self.timestamps = ActivityTimestamps.optional(resp.get("timestamps"))
        self.application_id = Snowflake.optional(resp.get("application_id"))
        self.details = resp.get("details")
        self.state = resp.get("state")
        self.emoji = ActivityEmoji.optional(resp.get("emoji"))
        self.party = ActivityParty.optional(resp.get("party"))
        self.assets = ActivityAssets.optional(resp.get("assets"), self.application_id)
        self.secrets = ActivitySecrets.optional(resp.get("secrets"))
        self.instance = resp.get("instance")
        self.__flags = resp.get("flags")
        self.flags = (
            ActivityFlags.from_value(self.__flags) if self.__flags else self.__flags
        )
        self.buttons = resp.get("buttons")

    def to_dict(self):
        ret = {"name": self.name, "type": int(self.type)}
        if self.url:
            ret["url"] = self.url
        if self.created_at:
            ret["created_at"] = self.created_at.timestamp()
        if self.timestamps:
            ret["timestamps"] = self.timestamps.to_dict()
        if self.application_id:
            ret["application_id"] = str(self.application_id)
        if self.details:
            ret["details"] = self.details
        if self.state:
            ret["state"] = self.state
        if self.emoji:
            ret["emoji"] = self.emoji.to_dict()
        if self.party:
            ret["party"] = self.party.to_dict()
        if self.assets:
            ret["assets"] = self.assets.to_dict()
        if self.secrets:
            ret["secrets"] = self.secrets.to_dict()
        if self.instance:
            ret["instance"] = self.instance
        if self.flags:
            ret["flags"] = int(self.flags)
        if self.buttons:
            ret["buttons"] = self.buttons.to_dict()
        return ret


class ActivityTypes(TypeBase):
    GAME = 0
    STREAMING = 1
    LISTENING = 2
    WATCHING = 3
    CUSTOM = 4
    COMPETING = 5


class ActivityTimestamps:
    def __init__(self, resp):
        self.__start = resp.get("start")
        self.start = (
            datetime.datetime.fromtimestamp(self.__start / 1000)
            if self.__start
            else self.__start
        )
        self.__end = resp.get("end")
        self.end = (
            datetime.datetime.fromtimestamp(self.__end / 1000)
            if self.__end
            else self.__end
        )

    def to_dict(self):
        ret = {}
        if self.start:
            ret["start"] = self.start.timestamp()
        if self.end:
            ret["end"] = self.end.timestamp()
        return ret

    @classmethod
    def optional(cls, resp):
        if resp:
            return cls(resp)


class ActivityEmoji:
    def __init__(self, resp):
        self.name = resp["name"]
        self.id = Snowflake.optional(resp.get("id"))
        self.animated = resp.get("animated", False)

    def to_dict(self):
        ret = {"name": self.name}
        if self.id:
            ret["id"] = str(self.id)
        if self.animated:
            ret["animated"] = self.animated
        return ret

    @classmethod
    def optional(cls, resp):
        if resp:
            return cls(resp)


class ActivityParty:
    def __init__(self, resp):
        self.id = resp.get("id")
        self.size = resp.get("size")

    def to_dict(self):
        ret = {}
        if self.id:
            ret["id"] = str(self.id)
        if self.size:
            ret["size"] = self.size
        return ret

    @classmethod
    def optional(cls, resp):
        if resp:
            return cls(resp)


class ActivityAssets:
    def __init__(self, resp, application_id):
        self.application_id = application_id
        self.large_image = resp.get("large_image")
        self.large_text = resp.get("large_text")
        self.small_image = resp.get("small_image")
        self.small_text = resp.get("small_text")

    def large_image_url(
        self, *, extension: str = "webp", size: int = 1024
    ) -> typing.Optional[str]:
        if self.large_image:
            return cdn_url(
                "app-assets/{application_id}",
                image_hash=self.large_image,
                extension=extension,
                size=size,
                application_id=self.application_id,
            )

    def small_image_url(
        self, *, extension: str = "webp", size: int = 1024
    ) -> typing.Optional[str]:
        if self.small_image:
            return cdn_url(
                "app-assets/{application_id}",
                image_hash=self.small_image,
                extension=extension,
                size=size,
                application_id=self.application_id,
            )

    def to_dict(self):
        ret = {}
        if self.large_image:
            ret["large_image"] = self.large_image
        if self.large_text:
            ret["large_text"] = self.large_text
        if self.small_image:
            ret["small_image"] = self.small_image
        if self.small_text:
            ret["small_text"] = self.small_text
        return ret

    @classmethod
    def optional(cls, resp, application_id):
        if resp:
            return cls(resp, application_id)


class ActivitySecrets:
    def __init__(self, resp):
        self.join = resp.get("join")
        self.spectate = resp.get("spectate")
        self.match = resp.get("match")

    def to_dict(self):
        ret = {}
        if self.join:
            ret["join"] = self.join
        if self.spectate:
            ret["spectate"] = self.spectate
        if self.match:
            ret["match"] = self.match
        return ret

    @classmethod
    def optional(cls, resp):
        if resp:
            return cls(resp)


class ActivityFlags(FlagBase):
    INSTANCE = 1 << 0
    JOIN = 1 << 1
    SPECTATE = 1 << 2
    JOIN_REQUEST = 1 << 3
    SYNC = 1 << 4
    PLAY = 1 << 5


class ActivityButtons:
    def __init__(self, resp):
        self.label = resp["label"]
        self.url = resp["url"]

    def to_dict(self):
        return {"label": self.label, "url": self.url}

    @classmethod
    def optional(cls, resp):
        if resp:
            return cls(resp)


# https://discord.com/developers/docs/topics/opcodes-and-status-codes#gateway


class Opcodes:
    DISPATCH = 0
    HEARTBEAT = 1
    IDENTIFY = 2
    PRESENCE_UPDATE = 3
    VOICE_STATE_UPDATE = 4
    RESUME = 6
    RECONNECT = 7
    REQUEST_GUILD_MEMBERS = 8
    INVALID_SESSION = 9
    HELLO = 10
    HEARTBEAT_ACK = 11

    @staticmethod
    def as_string(code: int) -> str:
        opcodes = {
            0: "Dispatch",
            1: "Heartbeat",
            2: "Identify",
            3: "Presence Update",
            4: "Voice State Update",
            6: "Resume",
            7: "Reconnect",
            8: "Request Guild Members",
            9: "Invalid Session",
            10: "Hello",
            11: "Heartbeat ACK",
        }
        return opcodes.get(code)
