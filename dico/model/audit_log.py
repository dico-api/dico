import typing
from .channel import Channel
from .guild import Integration
from .snowflake import Snowflake
from .user import User
from .webhook import Webhook
from ..base.model import TypeBase

if typing.TYPE_CHECKING:
    from ..api import APIClient
    from .channel import Message
    from .permission import Role


class AuditLog:
    RESPONSE = typing.Union["AuditLog", typing.Awaitable["AuditLog"]]

    def __init__(self, client: "APIClient", resp: dict):
        self.client: "APIClient" = client
        self.raw: dict = resp
        self.webhooks: typing.List[Webhook] = [Webhook(client, x) for x in resp["webhooks"]]
        self.users: typing.List[User] = [User.create(client, x) for x in resp["users"]]
        self.audit_log_entries: typing.List[AuditLogEntry] = [AuditLogEntry(client, x) for x in resp["audit_log_entries"]]
        self.integrations: typing.List[Integration] = [Integration(client, x) for x in resp["integrations"]]
        self.threads: typing.List[Channel] = [Channel.create(client, x) for x in resp["threads"]]


class AuditLogEntry:
    def __init__(self, client: "APIClient", resp: dict):
        self.client: "APIClient" = client
        self.raw: dict = resp
        self.target_id: typing.Optional[str] = resp.get("target_id")  # or is this snowflake?
        self.changes: typing.List[AuditLogChange] = [AuditLogChange(client, x) for x in resp.get("changes", [])]
        self.user_id: typing.Optional[Snowflake] = Snowflake.optional(resp.get("user_id"))
        self.id: Snowflake = Snowflake(resp["id"])
        self.action_type: AuditLogEvents = AuditLogEvents(int(resp["action_type"]))
        self.__options = resp.get("options")
        self.options: typing.Optional[OptionalAuditEntryInfo] = OptionalAuditEntryInfo(self.client, self.__options) if self.__options else self.__options
        self.reason: typing.Optional[str] = resp.get("reason")

    @property
    def user(self) -> typing.Optional[User]:
        if self.user_id and self.client.has_cache:
            return self.client.get(self.user_id, "user")


class AuditLogEvents(TypeBase):
    GUILD_UPDATE = 1

    CHANNEL_CREATE = 10
    CHANNEL_UPDATE = 11
    CHANNEL_DELETE = 12
    CHANNEL_OVERWRITE_CREATE = 13
    CHANNEL_OVERWRITE_UPDATE = 14
    CHANNEL_OVERWRITE_DELETE = 15

    MEMBER_KICK = 20
    MEMBER_PRUNE = 21
    MEMBER_BAN_ADD = 22
    MEMBER_BAN_REMOVE = 23
    MEMBER_UPDATE = 24
    MEMBER_ROLE_UPDATE = 25
    MEMBER_MOVE = 26
    MEMBER_DISCONNECT = 27
    BOT_ADD = 28

    ROLE_CREATE = 30
    ROLE_UPDATE = 31
    ROLE_DELETE = 32

    INVITE_CREATE = 40
    INVITE_UPDATE = 41
    INVITE_DELETE = 42

    WEBHOOK_CREATE = 50
    WEBHOOK_UPDATE = 51
    WEBHOOK_DELETE = 52

    EMOJI_CREATE = 60
    EMOJI_UPDATE = 61
    EMOJI_DELETE = 62

    MESSAGE_DELETE = 72
    MESSAGE_BULK_DELETE = 73
    MESSAGE_PIN = 74
    MESSAGE_UNPIN = 75

    INTEGRATION_CREATE = 80
    INTEGRATION_UPDATE = 81
    INTEGRATION_DELETE = 82

    STAGE_INSTANCE_CREATE = 83
    STAGE_INSTANCE_UPDATE = 84
    STAGE_INSTANCE_DELETE = 85

    STICKER_CREATE = 90
    STICKER_UPDATE = 91
    STICKER_DELETE = 92

    THREAD_CREATE = 110
    THREAD_UPDATE = 111
    THREAD_DELETE = 112


class OptionalAuditEntryInfo:
    def __init__(self, client: "APIClient", resp: dict):
        self.raw: dict = resp
        self.client: "APIClient" = client
        self.delete_member_days: typing.Optional[str] = resp.get("delete_member_days")
        self.members_removed: typing.Optional[str] = resp.get("members_removed")
        self.channel_id: typing.Optional[Snowflake] = Snowflake.optional(resp.get("channel_id"))
        self.message_id: typing.Optional[Snowflake] = Snowflake.optional(resp.get("message_id"))
        self.count: typing.Optional[str] = resp.get("count")
        self.id: typing.Optional[Snowflake] = Snowflake.optional(resp.get("id"))
        self.type: typing.Optional[str] = resp.get("type")
        self.role_name: typing.Optional[str] = resp.get("role_name")

    @property
    def channel(self) -> typing.Optional[Channel]:
        if self.channel_id and self.client.has_cache:
            return self.client.get(self.channel_id, "channel")

    @property
    def message(self) -> typing.Optional["Message"]:
        if self.message_id and self.client.has_cache:
            return self.client.get(self.message_id, "message")

    @property
    def overwrite_entry(self) -> typing.Optional[typing.Union["Role", User]]:
        if self.id and self.client.has_cache:
            return self.client.get(self.id, "role" if self.type == "0" else "user" if self.type == "1" else None)


class AuditLogChange:
    def __init__(self, client: "APIClient", resp: dict):
        self.raw: dict = resp
        self.client: "APIClient" = client
        self.key: str = resp["key"]
        self.new_value: typing.Optional[dict] = resp.get("new_value")
        self.old_value: typing.Optional[dict] = resp.get("old_value")

    @property
    def new(self) -> typing.Optional["AuditLogChanges"]:
        if self.new_value:
            return AuditLogChanges(self.client, self.new_value)

    @property
    def old(self) -> typing.Optional["AuditLogChanges"]:
        if self.old_value:
            return AuditLogChanges(self.client, self.old_value)


class AuditLogChanges:
    def __init__(self, client: "APIClient", resp: dict):
        self.raw: dict = resp
        self.client: "APIClient" = client

        # any
        self.name: str = resp["name"]
        self.id: Snowflake = Snowflake(resp["id"])
        self.type: typing.Union[int, str] = resp["type"]

        self.description: typing.Optional[str] = resp.get("description")
        self.icon_hash: typing.Optional[str] = resp.get("icon_hash")
        self.splash_hash: typing.Optional[str] = resp.get("splash_hash")
        self.discovery_splash_hash: typing.Optional[str] = resp.get("discovery_splash_hash")
        self.banner_hash: typing.Optional[str] = resp.get("banner_hash")
        self.owner_id: typing.Optional[Snowflake] = Snowflake.optional(resp.get("owner_id"))
        self.region: typing.Optional[str] = resp.get("region")
        self.preferred_locale: typing.Optional[str] = resp.get("preferred_locale")
        self.afk_channel_id: typing.Optional[Snowflake] = Snowflake.optional(resp.get("afk_channel_id"))
        self.afk_timeout: typing.Optional[int] = resp.get("afk_timeout")
        self.rules_channel_id: typing.Optional[Snowflake] = Snowflake.optional(resp.get("rules_channel_id"))
        self.public_updates_channel_id: typing.Optional[Snowflake] = Snowflake.optional(resp.get("public_updates_channel_id"))
        self.mfa_level: typing.Optional[int] = resp.get("mfa_level")
        self.verification_level: typing.Optional[int] = resp.get("verification_level")
        self.explicit_content_filter: typing.Optional[int] = resp.get("explicit_content_filter")
        self.default_message_notifications: typing.Optional[int] = resp.get("default_message_notifications")
        self.vanity_url_code: typing.Optional[str] = resp.get("vanity_url_code")
        self.add: typing.Optional[typing.List[dict]] = resp.get("$add")
        self.remove: typing.Optional[typing.List[dict]] = resp.get("$remove")
        self.prune_delete_days: typing.Optional[int] = resp.get("prune_delete_days")
        self.widget_enabled: typing.Optional[bool] = resp.get("widget_enabled")
        self.widget_channel_id: typing.Optional[Snowflake] = Snowflake.optional(resp.get("widget_channel_id"))
        self.system_channel_id: typing.Optional[Snowflake] = Snowflake.optional(resp.get("system_channel_id"))

        self.position: typing.Optional[int] = resp.get("position")
        self.topic: typing.Optional[str] = resp.get("topic")
        self.bitrate: typing.Optional[int] = resp.get("bitrate")
        self.permission_overwrites: typing.Optional[typing.List[dict]] = resp.get("permission_overwrites")
        self.nsfw: typing.Optional[bool] = resp.get("nsfw")
        self.application_id: typing.Optional[Snowflake] = Snowflake.optional(resp.get("application_id"))
        self.rate_limit_per_user: typing.Optional[int] = resp.get("rate_limit_per_user")

        self.permissions: typing.Optional[str] = resp.get("permissions")
        self.color: typing.Optional[int] = resp.get("color")
        self.hoist: typing.Optional[bool] = resp.get("hoist")
        self.mentionable: typing.Optional[bool] = resp.get("mentionable")
        self.allow: typing.Optional[str] = resp.get("allow")
        self.deny: typing.Optional[str] = resp.get("deny")

        self.code: typing.Optional[str] = resp.get("code")
        self.channel_id: typing.Optional[Snowflake] = Snowflake.optional(resp.get("channel_id"))
        self.inviter_id: typing.Optional[Snowflake] = Snowflake.optional(resp.get("inviter_id"))
        self.max_uses: typing.Optional[int] = resp.get("max_uses")
        self.uses: typing.Optional[int] = resp.get("uses")
        self.max_age: typing.Optional[int] = resp.get("max_age")
        self.temporary: typing.Optional[bool] = resp.get("temporary")

        self.deaf: typing.Optional[bool] = resp.get("deaf")
        self.mute: typing.Optional[bool] = resp.get("mute")
        self.nick: typing.Optional[str] = resp.get("nick")
        self.avatar_hash: typing.Optional[str] = resp.get("avatar_hash")

        self.enable_emoticons: typing.Optional[bool] = resp.get("enable_emoticons")
        self.expire_behavior: typing.Optional[int] = resp.get("expire_behavior")
        self.expire_grace_period: typing.Optional[int] = resp.get("expire_grace_period")
        self.user_limit: typing.Optional[int] = resp.get("user_limit")
        self.privacy_level: typing.Optional[int] = resp.get("privacy_level")

        self.tags: typing.Optional[str] = resp.get("tags")
        self.format_type: typing.Optional[int] = resp.get("format_type")
        self.asset: typing.Optional[str] = resp.get("asset")
        self.available: typing.Optional[bool] = resp.get("available")
        self.guild_id: typing.Optional[Snowflake] = Snowflake.optional(resp.get("guild_id"))

        self.archived: typing.Optional[bool] = resp.get("archived")
        self.locked: typing.Optional[bool] = resp.get("locked")
        self.auto_archive_duration: typing.Optional[int] = resp.get("auto_archive_duration")

        self.default_auto_archive_duration: typing.Optional[int] = resp.get("default_auto_archive_duration")
