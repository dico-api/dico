import typing
from .snowflake import Snowflake
from .user import User
from ..base.model import FlagBase


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
        self.op = resp["op"]
        self.d = resp.get("d", {})
        self.s = resp.get("s")
        self.t = resp.get("t")

    def to_dict(self):
        return {"op": self.op, "d": self.d, "s": self.s, "t": self.t}


class Application:
    def __init__(self, client, resp):
        print(resp)
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

        client.application = self


class ApplicationFlags(FlagBase):
    GATEWAY_PRESENCE = 1 << 12
    GATEWAY_PRESENCE_LIMITED = 1 << 13
    GATEWAY_GUILD_MEMBERS = 1 << 14
    GATEWAY_GUILD_MEMBERS_LIMITED = 1 << 15
    VERIFICATION_PENDING_GUILD_LIMIT = 1 << 16
    EMBEDDED = 1 << 17


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
