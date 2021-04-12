import typing


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


class GatewayResponse:
    def __init__(self, resp: dict):
        self.op = resp["op"]
        self.d = resp.get("d", {})
        self.s = resp.get("s")
        self.t = resp.get("t")

    def to_dict(self):
        return {"op": self.op, "d": self.d, "s": self.s, "t": self.t}


class ReadyEvent:
    def __init__(self, resp: dict):
        self.v = resp["v"]
        self.user = resp["user"]
        self.private_channels = resp["private_channels"]
        self.guilds = resp["guilds"]
        self.session_id = resp["session_id"]
        self.shard = resp.get("shard", [])
        self.application = resp["application"]


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
