import typing

from .snowflake import Snowflake
from ..base.model import DiscordObjectBase, FlagBase
from ..utils import cdn_url

if typing.TYPE_CHECKING:
    from .guild import Guild
    from ..api import APIClient


class PermissionFlags(FlagBase):
    CREATE_INSTANT_INVITE = 1 << 0
    KICK_MEMBERS = 1 << 1
    BAN_MEMBERS = 1 << 2
    ADMINISTRATOR = 1 << 3
    MANAGE_CHANNELS = 1 << 4
    MANAGE_GUILD = 1 << 5
    ADD_REACTIONS = 1 << 6
    VIEW_AUDIT_LOG = 1 << 7
    PRIORITY_SPEAKER = 1 << 8
    STREAM = 1 << 9
    VIEW_CHANNEL = 1 << 10
    SEND_MESSAGES = 1 << 11
    SEND_TTS_MESSAGES = 1 << 12
    MANAGE_MESSAGES = 1 << 13
    EMBED_LINKS = 1 << 14
    ATTACH_FILES = 1 << 15
    READ_MESSAGE_HISTORY = 1 << 16
    MENTION_EVERYONE = 1 << 17
    USE_EXTERNAL_EMOJIS = 1 << 18
    VIEW_GUILD_INSIGHTS = 1 << 19
    CONNECT = 1 << 20
    SPEAK = 1 << 21
    MUTE_MEMBERS = 1 << 22
    DEAFEN_MEMBERS = 1 << 23
    MOVE_MEMBERS = 1 << 24
    USE_VAD = 1 << 25
    CHANGE_NICKNAME = 1 << 26
    MANAGE_NICKNAMES = 1 << 27
    MANAGE_ROLES = 1 << 28
    MANAGE_WEBHOOKS = 1 << 29
    MANAGE_EMOJIS_AND_STICKERS = 1 << 30
    USE_APPLICATION_COMMANDS = 1 << 31
    REQUEST_TO_SPEAK = 1 << 32
    MANAGE_EVENTS = 1 << 33
    MANAGE_THREADS = 1 << 34
    USE_PUBLIC_THREADS = 1 << 35
    USE_PRIVATE_THREADS = 1 << 36
    USE_EXTERNAL_STICKERS = 1 << 37
    SEND_MESSAGES_IN_THREADS = 1 << 38
    START_EMBEDDED_ACTIVITIES = 1 << 39
    MODERATE_MEMBERS = 1 << 40


class Role(DiscordObjectBase):
    TYPING = typing.Union[int, str, Snowflake, "Role"]
    RESPONSE = typing.Union["Role", typing.Awaitable["Role"]]
    RESPONSE_AS_LIST = typing.Union[
        typing.List["Role"], typing.Awaitable[typing.List["Role"]]
    ]
    _cache_type = "role"

    def __init__(self, client: "APIClient", resp: dict, *, guild_id: Snowflake = None):
        super().__init__(client, resp)
        self.guild_id: typing.Optional[Snowflake] = Snowflake.optional(
            guild_id
        )  # This isn't actually in payload, but role is always created at the guild, so why not?
        self.name: str = resp["name"]
        self.color: int = resp["color"]
        self.hoist: bool = resp["hoist"]
        self.icon: typing.Optional[str] = resp.get("icon")
        self.unicode_emoji: typing.Optional[str] = resp.get("unicode_emoji")
        self.position: int = resp["position"]
        self.permissions: PermissionFlags = PermissionFlags.from_value(
            int(resp["permissions"])
        )
        self.managed: bool = resp["managed"]
        self.mentionable: bool = resp["mentionable"]
        self.tags: typing.Optional[RoleTags] = RoleTags.optional(resp.get("tags"))

    @property
    def guild(self) -> typing.Optional["Guild"]:
        if self.client.has_cache:
            return self.client.get(self.guild_id, "guild")

    def to_position_param(self, position: int = None) -> dict:
        body = {"id": str(self.id)}
        if position is not None:
            body["position"] = position
        return body

    def icon_url(
        self, *, extension: str = "webp", size: int = 1024
    ) -> typing.Optional[str]:
        return cdn_url(
            "role-icons/{role_id}",
            image_hash=self.icon,
            extension=extension,
            size=size,
            role_id=self.id,
        )

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id} name={self.name}>"


class RoleTags:
    def __init__(self, resp: dict):
        self.bot_id: typing.Optional[Snowflake] = Snowflake.optional(resp.get("bot_id"))
        self.integration_id: typing.Optional[Snowflake] = Snowflake.optional(
            resp.get("integration_id")
        )
        self.premium_subscriber: bool = "premium_subscriber" in resp

    @classmethod
    def optional(cls, resp):
        if resp:
            return cls(resp)
