import datetime

from .channel import Channel
from .permission import Role, PermissionFlags
from .snowflake import Snowflake
from .user import User
from ..utils import cdn_url
from ..base.model import DiscordObjectBase


class Guild(DiscordObjectBase):
    def __init__(self, client, resp):
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
        self.verification_level = resp["verification_level"]
        self.default_message_notifications = resp["default_message_notifications"]
        self.explicit_content_filter = resp["explicit_content_filter"]
        self.roles = [Role.create(client, x, guild_id=self.id) for x in resp["roles"]]
        self.emojis = resp["emojis"]
        self.features = resp["features"]
        self.mfa_level = resp["mfa_level"]
        self.application_id = Snowflake.optional(resp["application_id"])
        self.system_channel_id = Snowflake.optional(resp["system_channel_id"])
        self.system_channel_flags = resp["system_channel_flags"]
        self.rules_channel_id = Snowflake.optional(resp["rules_channel_id"])
        self.__joined_at = resp["joined_at"]
        self.large = resp.get("large", False)
        self.unavailable = resp.get("unavailable", False)
        self.member_count = resp.get("member_count", 0)
        self.voice_states = resp.get("voice_states", [])
        self.members = resp.get("members", [])
        self.channels = [Channel.create(client, x, guild_id=self.id) for x in resp.get("channels", [])]
        self.presences = resp.get("presences", [])
        self.max_presences = resp.get("max_presences", 25000)
        self.max_members = resp.get("max_members")
        self.vanity_url_code = resp["vanity_url_code"]
        self.description = resp["description"]
        self.banner = resp["banner"]
        self.premium_tier = resp["premium_tier"]
        self.premium_subscription_count = resp.get("premium_subscription_count", 0)
        self.preferred_locale = resp["preferred_locale"]
        self.public_updates_channel_id = Snowflake.optional(resp["public_updates_channel_id"])
        self.max_video_channel_users = resp.get("max_video_channel_users")
        self.approximate_member_count = resp.get("approximate_member_count")
        self.approximate_presence_count = resp.get("approximate_presence_count")
        self.welcome_screen = resp.get("welcome_screen")
        self.nsfw = resp["nsfw"]

        self.joined_at = datetime.datetime.fromisoformat(self.__joined_at) if self.__joined_at else self.__joined_at

        self.cache = client.cache.get_guild_container(self.id)

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
        return self.cache.get

    @property
    def get_user(self):
        return self.cache.get_storage("user").get

    @property
    def get_channel(self):
        return self.cache.get_storage("channel").get

    @property
    def get_role(self):
        return self.cache.get_storage("role").get

    def get_owner(self):
        return self.get_user(self.owner_id)


class Member:
    def __init__(self, client, resp, *, user: User = None):
        self.user = user
        self.__user = resp.get("user")
        self.nick = resp.get("nick")
        self.roles = [client.get(x) for x in resp["roles"]]
        self.joined_at = datetime.datetime.fromisoformat(resp["joined_at"])
        self.__premium_since = resp.get("premium_since")
        self.deaf = resp["deaf"]
        self.mute = resp["mute"]
        self.pending = resp.get("pending", False)
        self.__permissions = resp.get("permissions")

        if self.__user and not self.user:
            self.user = User.create(client, resp)

        if self.__premium_since:
            self.premium_since = datetime.datetime.fromisoformat(self.__premium_since)

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
            pass
        else:
            return PermissionFlags.from_value(0)
