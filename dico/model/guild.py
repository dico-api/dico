import datetime

from .emoji import Emoji
from .permission import Role, PermissionFlags
from .snowflake import Snowflake
from .user import User
from ..utils import cdn_url
from ..base.model import DiscordObjectBase, TypeBase, FlagBase


class Guild(DiscordObjectBase):
    def __init__(self, client, resp):
        from .channel import Channel  # Prevent circular import.
        super().__init__(client, resp)
        self._cache_type = "guild"
        self.name = resp["name"]
        self.icon = resp["icon"]
        self.icon_hash = resp.get("icon_hash")
        self.splash = resp["splash"]
        self.discovery_splash = resp["discovery_splash"]
        self.owner = resp.get("owner", False)
        self.owner_id = Snowflake(resp["owner_id"])
        self.permissions = resp.get("permissions")
        self.region = resp["region"]
        self.afk_channel_id = Snowflake.optional(resp["afk_channel_id"])
        self.afk_timeout = resp["afk_timeout"]
        self.widget_enabled = resp.get("widget_enabled")
        self.widget_channel_id = Snowflake.optional(resp.get("widget_channel_id"))
        self.verification_level = VerificationLevel(resp["verification_level"])
        self.default_message_notifications = DefaultMessageNotificationLevel(resp["default_message_notifications"])
        self.explicit_content_filter = ExplicitContentFilterLevel(resp["explicit_content_filter"])
        self.roles = [Role.create(client, x, guild_id=self.id) for x in resp["roles"]]
        self.emojis = [Emoji(self.client, x) for x in resp["emojis"]]
        self.features = resp["features"]
        self.mfa_level = MFALevel(resp["mfa_level"])
        self.application_id = Snowflake.optional(resp["application_id"])
        self.system_channel_id = Snowflake.optional(resp["system_channel_id"])
        self.system_channel_flags = SystemChannelFlags.from_value(resp["system_channel_flags"])
        self.rules_channel_id = Snowflake.optional(resp["rules_channel_id"])
        self.__joined_at = resp["joined_at"]
        self.joined_at = datetime.datetime.fromisoformat(self.__joined_at) if self.__joined_at else self.__joined_at
        self.large = resp.get("large", False)
        self.unavailable = resp.get("unavailable", False)
        self.member_count = resp.get("member_count", 0)
        self.voice_states = resp.get("voice_states", [])
        self.members = [Member.create(self.client, x, guild_id=self.id) for x in resp.get("members", [])]
        self.channels = [Channel.create(client, x, guild_id=self.id) for x in resp.get("channels", [])]
        self.presences = resp.get("presences", [])
        self.max_presences = resp.get("max_presences", 25000)
        self.max_members = resp.get("max_members")
        self.vanity_url_code = resp["vanity_url_code"]
        self.description = resp["description"]
        self.banner = resp["banner"]
        self.premium_tier = PremiumTier(resp["premium_tier"])
        self.premium_subscription_count = resp.get("premium_subscription_count", 0)
        self.preferred_locale = resp["preferred_locale"]
        self.public_updates_channel_id = Snowflake.optional(resp["public_updates_channel_id"])
        self.max_video_channel_users = resp.get("max_video_channel_users")
        self.approximate_member_count = resp.get("approximate_member_count")
        self.approximate_presence_count = resp.get("approximate_presence_count")
        self.welcome_screen = resp.get("welcome_screen")
        self.nsfw = resp["nsfw"]

        self.cache = client.cache.get_guild_container(self.id) if client.has_cache else None

    def icon_url(self, *, extension="webp", size=1024):
        if self.icon:
            return cdn_url("icons/{guild_id}", image_hash=self.icon, extension=extension, size=size, guild_id=self.id)

    def splash_url(self, *, extension="webp", size=1024):
        if self.splash:
            return cdn_url("splashes/{guild_id}", image_hash=self.splash, extension=extension, size=size, guild_id=self.id)

    def discovery_splash_url(self, *, extension="webp", size=1024):
        if self.discovery_splash:
            return cdn_url("discovery-splashes/{guild_id}", image_hash=self.discovery_splash, extension=extension, size=size, guild_id=self.id)

    def banner_url(self, *, extension="webp", size=1024):
        if self.banner:
            return cdn_url("banners/{guild_id}", image_hash=self.banner, extension=extension, size=size, guild_id=self.id)

    @property
    def get(self):
        """Alias of ``Guild.cache.get``."""
        if self.cache:
            return self.cache.get

    def get_owner(self):
        if self.cache:
            return self.get(self.owner_id, "member") or self.get(self.owner_id, "user")


class DefaultMessageNotificationLevel(TypeBase):
    ALL_MESSAGES = 0
    ONLY_MENTIONS = 1


class ExplicitContentFilterLevel(TypeBase):
    DISABLED = 0
    MEMBERS_WITHOUT_ROLES = 1
    ALL_MEMBERS = 2


class MFALevel(TypeBase):
    NONE = 0
    ELEVATED = 1


class VerificationLevel(TypeBase):
    NONE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    VERY_HIGH = 4


class PremiumTier(TypeBase):
    NONE = 0
    TIER_1 = 1
    TIER_2 = 2
    TIER_3 = 3


class SystemChannelFlags(FlagBase):
    SUPPRESS_JOIN_NOTIFICATIONS = 1 << 0
    SUPPRESS_PREMIUM_SUBSCRIPTIONS = 1 << 1
    SUPPRESS_GUILD_REMINDER_NOTIFICATIONS = 1 << 2


class GuildPreview:
    def __init__(self, client, resp):
        self.id = Snowflake(resp["id"])
        self.name = resp["name"]
        self.icon = resp["icon"]
        self.splash = resp["splash"]
        self.discovery_splash = resp["discovery_splash"]
        self.emojis = [Emoji(client, x) for x in resp["emojis"]]
        self.features = resp["features"]
        self.approximate_member_count = resp["approximate_member_count"]
        self.approximate_presence_count = resp["approximate_presence_count"]
        self.description = resp["description"]


class GuildWidget:
    def __init__(self, resp):
        self.enabled = resp["enabled"]
        self.channel_id = Snowflake.optional(resp["channel_id"])


class Member:
    def __init__(self, client, resp, *, user: User = None, guild_id=None):
        self.raw = resp
        self.client = client
        self.user = user
        self.__user = resp.get("user")
        self.user = User.create(client, self.__user) if self.__user and not self.user else self.user if self.user else self.__user
        self.nick = resp.get("nick")
        self.roles = [client.get(x) for x in resp["roles"]] if client.has_cache else [Snowflake(x) for x in resp["roles"]]
        self.joined_at = datetime.datetime.fromisoformat(resp["joined_at"])
        self.__premium_since = resp.get("premium_since")
        self.premium_since = datetime.datetime.fromisoformat(self.__premium_since) if self.__premium_since else self.__premium_since
        self.deaf = resp.get("deaf", False)
        self.mute = resp.get("mute", False)
        self.pending = resp.get("pending", False)
        self.__permissions = resp.get("permissions")
        self.guild_id = Snowflake.optional(resp.get("guild_id")) or Snowflake.ensure_snowflake(guild_id)

    def __str__(self):
        return self.nick or (self.user.username if self.user else None)

    def __int__(self):
        if self.user:
            return self.user.id

    @property
    def mention(self):
        if self.user:
            return f"<@!{self.user.id}>"

    @property
    def permissions(self):
        if self.__permissions:
            return PermissionFlags.from_value(int(self.__permissions))
        elif self.roles:
            raise NotImplementedError
        else:
            return PermissionFlags.from_value(0)

    @classmethod
    def create(cls, client, resp, *, user=None, guild_id=None, cache: bool = True):
        if cache and client.has_cache and (guild_id or resp.get("guild_id")) and (user or resp.get("user")):
            _guild_id = guild_id or resp.get("guild_id")
            _user_id = user.id if isinstance(user, User) else resp["user"]["id"]
            maybe_exist = client.cache.get_guild_container(_guild_id).get_storage("member").get(_user_id)
            if maybe_exist:
                orig = maybe_exist.raw
                for k, v in resp.items():
                    if orig.get(k) != v:
                        orig[k] = v
                maybe_exist.__init__(client, orig, user=user, guild_id=guild_id)
                return maybe_exist
        ret = cls(client, resp, user=user, guild_id=guild_id)
        if cache and client.has_cache and ret.guild_id and ret.user:
            client.cache.get_guild_container(ret.guild_id).add(ret.user.id, "member", ret)
        return ret
