import typing
import datetime
from .snowflake import Snowflake
from .user import User
from ..base.model import FlagBase, TypeBase


class GetGateway:
    def __init__(self, resp: dict):
        self.url: str = resp["url"]
        self.shards: typing.Optional[int] = resp.get("shards", 0)
        self.session_start_limit: typing.Optional[SessionStartLimit] = SessionStartLimit.optional(resp.get("session_start_limit"))

    def to_dict(self):
        return {"url": self.url, "shards": self.shards, "session_start_limit": self.session_start_limit}


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
        return {"total": self.total, "remaining": self.remaining, "reset_after": self.reset_after, "max_concurrency": self.max_concurrency}


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

    @classmethod
    def full(cls):
        return cls(*[x for x in dir(cls) if isinstance(getattr(cls, x), int)])

    @classmethod
    def no_privileged(cls):
        ret = cls.full()
        ret.guild_presences = False
        ret.guild_members = False
        return ret


class GatewayResponse:
    def __init__(self, resp: dict):
        self.raw = resp
        self.op = resp["op"]
        self.d = resp.get("d", {})
        self.s = resp.get("s")
        self.t = resp.get("t")

    def to_dict(self):
        return {"op": self.op, "d": self.d, "s": self.s, "t": self.t}


class Application:
    TYPING = typing.Union[int, str, Snowflake, "Application"]

    def __init__(self, client, resp):
        self.id = Snowflake(resp["id"])
        self.name = resp["name"]
        self.icon = resp["icon"]
        self.description = resp["description"]
        self.rpc_origins = resp.get("rpc_origins")
        self.bot_public = resp["bot_public"]
        self.bot_require_code_grant = resp["bot_require_code_grant"]
        self.terms_of_service_url = resp.get("terms_of_service_url")
        self.privacy_policy_url = resp.get("privacy_policy_url")
        self.owner = User.create(client, resp["owner"])
        self.summary = resp["summary"]
        self.verify_key = resp["verify_key"]
        self.team = resp["team"]
        self.guild_id = resp["guild_id"]
        self.primary_sku_id = resp["primary_sku_id"]
        self.slug = resp["slug"]
        self.cover_image = resp["cover_image"]
        self.flags = ApplicationFlags.from_value(resp["flags"])

    def __int__(self):
        return int(self.id)


class ApplicationFlags(FlagBase):
    GATEWAY_PRESENCE = 1 << 12
    GATEWAY_PRESENCE_LIMITED = 1 << 13
    GATEWAY_GUILD_MEMBERS = 1 << 14
    GATEWAY_GUILD_MEMBERS_LIMITED = 1 << 15
    VERIFICATION_PENDING_GUILD_LIMIT = 1 << 16
    EMBEDDED = 1 << 17


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
        self.created_at = datetime.datetime.fromtimestamp(self.__created_at/1000) if self.__created_at else self.__created_at
        self.timestamps = ActivityTimestamps.optional(resp.get("timestamps"))
        self.application_id = Snowflake.optional(resp.get("application_id"))
        self.details = resp.get("details")
        self.state = resp.get("state")
        self.emoji = ActivityEmoji.optional(resp.get("emoji"))
        self.party = ActivityParty.optional(resp.get("party"))
        self.assets = ActivityAssets.optional(resp.get("assets"))
        self.secrets = ActivitySecrets.optional(resp.get("secrets"))
        self.instance = resp.get("instance")
        self.__flags = resp.get("flags")
        self.flags = ActivityFlags.from_value(self.__flags) if self.__flags else self.__flags
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
        self.start = datetime.datetime.fromtimestamp(self.__start/1000) if self.__start else self.__start
        self.__end = resp.get("end")
        self.end = datetime.datetime.fromtimestamp(self.__end/1000) if self.__end else self.__end

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
    def __init__(self, resp):
        self.large_image = resp.get("large_image")
        self.large_text = resp.get("large_text")
        self.small_image = resp.get("small_image")
        self.small_text = resp.get("small_text")

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
    def optional(cls, resp):
        if resp:
            return cls(resp)


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
    def as_string(code: int):
        opcodes = {0: "Dispatch",
                   1: "Heartbeat",
                   2: "Identify",
                   3: "Presence Update",
                   4: "Voice State Update",
                   6: "Resume",
                   7: "Reconnect",
                   8: "Request Guild Members",
                   9: "Invalid Session",
                   10: "Hello",
                   11: "Heartbeat ACK"}
        return opcodes.get(code)
