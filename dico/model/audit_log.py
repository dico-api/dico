import typing
from .channel import Channel
from .guild import Integration
from .snowflake import Snowflake
from .user import User
from .webhook import Webhook
from ..base.model import TypeBase


class AuditLog:
    RESPONSE = typing.Union["AuditLog", typing.Awaitable["AuditLog"]]

    def __init__(self, client, resp):
        self.client = client
        self.raw = resp
        self.webhooks = [Webhook(client, x) for x in resp["webhooks"]]
        self.users = [User.create(client, x) for x in resp["users"]]
        self.audit_log_entries = [AuditLogEntry(client, x) for x in resp["audit_log_entries"]]
        self.integrations = [Integration(client, x) for x in resp["integrations"]]
        self.threads = [Channel.create(client, x) for x in resp["threads"]]


class AuditLogEntry:
    def __init__(self, client, resp):
        self.client = client
        self.raw = resp
        self.target_id = resp.get("target_id")
        self.changes = [AuditLogChange(client, x) for x in resp.get("changes", [])]
        self.user_id = Snowflake.optional(resp.get("user_id"))
        self.id = Snowflake(resp["id"])
        self.action_type = AuditLogEvents(int(resp["action_type"]))
        self.__options = resp.get("options")
        self.options = OptionalAuditEntryInfo(self.client, self.__options) if self.__options else self.__options
        self.reason = resp.get("reason")


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
    def __init__(self, client, resp):
        self.raw = resp
        self.client = client
        self.delete_member_days = resp.get("delete_member_days")
        self.members_removed = resp.get("members_removed")
        self.channel_id = Snowflake.optional(resp.get("channel_id"))
        self.message_id = Snowflake.optional(resp.get("message_id"))
        self.count = resp.get("count")
        self.id = Snowflake.optional(resp.get("id"))
        self.type = resp.get("type")
        self.role_name = resp.get("role_name")

    @property
    def channel(self):
        if self.channel_id and self.client.has_cache:
            return self.client.cache.get(self.channel_id, "channel")

    @property
    def message(self):
        if self.message_id and self.client.has_cache:
            return self.client.cache.get(self.message_id, "message")

    @property
    def overwrite_entry(self):
        if self.id and self.client.has_cache:
            return self.client.cache.get(self.id, "role" if self.type == "0" else "member" if self.type == "1" else None)


class AuditLogChange:
    def __init__(self, client, resp):
        self.raw = resp
        self.client = client
        self.key = resp["key"]
        self.new_value = resp.get("new_value")
        self.old_value = resp.get("old_value")

    @property
    def new(self):
        if self.new_value:
            return AuditLogChanges(self.client, self.new_value)

    @property
    def old(self):
        if self.old_value:
            return AuditLogChanges(self.client, self.old_value)


class AuditLogChanges:
    def __init__(self, client, resp):
        self.raw = resp
        self.client = client

        # any
        self.name = resp["name"]
        self.id = Snowflake(resp["id"])
        self.type = resp["type"]

        self.description = resp.get("description")
        self.icon_hash = resp.get("icon_hash")
        self.splash_hash = resp.get("splash_hash")
        self.discovery_splash_hash = resp.get("discovery_splash_hash")
        self.banner_hash = resp.get("banner_hash")
        self.owner_id = resp.get("owner_id")
        self.region = resp.get("region")
        self.preferred_locale = resp.get("preferred_locale")
        self.afk_channel_id = resp.get("afk_channel_id")
        self.afk_timeout = resp.get("afk_timeout")
        self.rules_channel_id = resp.get("rules_channel_id")
        self.public_updates_channel_id = resp.get("public_updates_channel_id")
        self.mfa_level = resp.get("mfa_level")
        self.verification_level = resp.get("verification_level")
        self.explicit_content_filter = resp.get("explicit_content_filter")
        self.default_message_notifications = resp.get("default_message_notifications")
        self.vanity_url_code = resp.get("vanity_url_code")
        self.add = resp.get("$add")
        self.remove = resp.get("$remove")
        self.prune_delete_days = resp.get("prune_delete_days")
        self.widget_enabled = resp.get("widget_enabled")
        self.widget_channel_id = resp.get("widget_channel_id")
        self.system_channel_id = resp.get("system_channel_id")

        self.position = resp.get("position")
        self.topic = resp.get("topic")
        self.bitrate = resp.get("bitrate")
        self.permission_overwrites = resp.get("permission_overwrites")
        self.nsfw = resp.get("nsfw")
        self.application_id = resp.get("application_id")
        self.rate_limit_per_user = resp.get("rate_limit_per_user")

        self.permissions = resp.get("permissions")
        self.color = resp.get("color")
        self.hoist = resp.get("hoist")
        self.mentionable = resp.get("mentionable")
        self.allow = resp.get("allow")
        self.deny = resp.get("deny")

        self.code = resp.get("code")
        self.channel_id = resp.get("channel_id")
        self.inviter_id = resp.get("inviter_id")
        self.max_uses = resp.get("max_uses")
        self.uses = resp.get("uses")
        self.max_age = resp.get("max_age")
        self.temporary = resp.get("temporary")

        self.deaf = resp.get("deaf")
        self.mute = resp.get("mute")
        self.nick = resp.get("nick")
        self.avatar_hash = resp.get("avatar_hash")

        self.enable_emoticons = resp.get("enable_emoticons")
        self.expire_behavior = resp.get("expire_behavior")
        self.expire_grace_period = resp.get("expire_grace_period")
        self.user_limit = resp.get("user_limit")
        self.privacy_level = resp.get("privacy_level")

        self.tags = resp.get("tags")
        self.format_type = resp.get("format_type")
        self.asset = resp.get("asset")
        self.available = resp.get("available")
        self.guild_id = resp.get("guild_id")

        self.archived = resp.get("archived")
        self.locked = resp.get("locked")
        self.auto_archive_duration = resp.get("auto_archive_duration")

        self.default_auto_archive_duration = resp.get("default_auto_archive_duration")
