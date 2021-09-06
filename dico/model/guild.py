import typing
import datetime

from .emoji import Emoji
from .permission import Role, PermissionFlags
from .snowflake import Snowflake
from .stage import StageInstance
from .sticker import Sticker
from .user import User
from ..utils import cdn_url
from ..base.model import DiscordObjectBase, TypeBase, FlagBase
from ..base.http import EmptyObject

if typing.TYPE_CHECKING:
    from .channel import Channel


class Guild(DiscordObjectBase):
    TYPING = typing.Union[int, str, Snowflake, "Guild"]
    RESPONSE = typing.Union["Guild", typing.Awaitable["Guild"]]
    RESPONSE_AS_LIST = typing.Union[typing.List["Guild"], typing.Awaitable[typing.List["Guild"]]]
    _cache_type = "guild"

    def __init__(self, client, resp):
        from .channel import Channel  # Prevent circular import.
        from .event import PresenceUpdate
        from .voice import VoiceState
        super().__init__(client, resp)
        self.name: str = resp["name"]
        self.icon: typing.Optional[str] = resp["icon"]
        self.icon_hash: typing.Optional[str] = resp.get("icon_hash")
        self.splash: typing.Optional[str] = resp["splash"]
        self.discovery_splash: typing.Optional[str] = resp["discovery_splash"]
        self.owner: typing.Optional[bool] = resp.get("owner")
        self.owner_id: Snowflake = Snowflake(resp["owner_id"])
        self.permissions: typing.Optional[str] = resp.get("permissions")
        self.region: typing.Optional[str] = resp["region"]
        self.afk_channel_id: typing.Optional[Snowflake] = Snowflake.optional(resp["afk_channel_id"])
        self.afk_timeout: int = resp["afk_timeout"]
        self.widget_enabled: typing.Optional[bool] = resp.get("widget_enabled")
        self.widget_channel_id: typing.Optional[Snowflake] = Snowflake.optional(resp.get("widget_channel_id"))
        self.verification_level: "VerificationLevel" = VerificationLevel(resp["verification_level"])
        self.default_message_notifications: "DefaultMessageNotificationLevel" = DefaultMessageNotificationLevel(resp["default_message_notifications"])
        self.explicit_content_filter: "ExplicitContentFilterLevel" = ExplicitContentFilterLevel(resp["explicit_content_filter"])
        self.roles: typing.List[Role] = [Role.create(client, x, guild_id=self.id) for x in resp["roles"]]
        self.emojis: typing.List[Emoji] = [Emoji(self.client, x) for x in resp["emojis"]]
        self.features: typing.List[str] = resp["features"]
        self.mfa_level: "MFALevel" = MFALevel(resp["mfa_level"])
        self.application_id: typing.Optional[Snowflake] = Snowflake.optional(resp["application_id"])
        self.system_channel_id: typing.Optional[Snowflake] = Snowflake.optional(resp["system_channel_id"])
        self.system_channel_flags: SystemChannelFlags = SystemChannelFlags.from_value(resp["system_channel_flags"])
        self.rules_channel_id: typing.Optional[Snowflake] = Snowflake.optional(resp["rules_channel_id"])
        self.__joined_at = resp.get("joined_at")
        self.joined_at: typing.Optional[datetime.datetime] = datetime.datetime.fromisoformat(self.__joined_at) if self.__joined_at else self.__joined_at
        self.large: typing.Optional[bool] = resp.get("large", False)
        self.unavailable: typing.Optional[bool] = resp.get("unavailable", False)
        self.member_count: typing.Optional[int] = resp.get("member_count", 0)
        self.voice_states: typing.Optional[typing.List[VoiceState]] = [VoiceState.create(client, x) for x in resp.get("voice_states", [])]
        self.members: typing.Optional[typing.List["GuildMember"]] = [GuildMember.create(self.client, x, guild_id=self.id) for x in resp.get("members", [])]
        self.channels: typing.Optional[typing.List[Channel]] = [Channel.create(client, x, guild_id=self.id) for x in resp.get("channels", [])]
        self.threads: typing.Optional[typing.List[Channel]] = [Channel.create(client, x, guild_id=self.id, ensure_cache_type="channel") for x in resp.get("threads", [])]
        self.presences: typing.Optional[typing.List[PresenceUpdate]] = [PresenceUpdate.create(client, x) for x in resp.get("presences", [])]
        self.max_presences: typing.Optional[int] = resp.get("max_presences")
        self.max_members: typing.Optional[int] = resp.get("max_members")
        self.vanity_url_code: typing.Optional[str] = resp["vanity_url_code"]
        self.description: typing.Optional[str] = resp["description"]
        self.banner: typing.Optional[str] = resp["banner"]
        self.premium_tier: "PremiumTier" = PremiumTier(resp["premium_tier"])
        self.premium_subscription_count: int = resp.get("premium_subscription_count", 0)
        self.preferred_locale: str = resp["preferred_locale"]
        self.public_updates_channel_id: typing.Optional[Snowflake] = Snowflake.optional(resp["public_updates_channel_id"])
        self.max_video_channel_users: typing.Optional[int] = resp.get("max_video_channel_users")
        self.approximate_member_count: typing.Optional[int] = resp.get("approximate_member_count")
        self.approximate_presence_count: typing.Optional[int] = resp.get("approximate_presence_count")
        self.__welcome_screen = resp.get("welcome_screen")
        self.welcome_screen: typing.Optional["WelcomeScreen"] = WelcomeScreen(self.__welcome_screen) if self.__welcome_screen else self.__welcome_screen
        self.nsfw_level: "NSFWLevel" = NSFWLevel(resp["nsfw_level"])
        self.stage_instances: typing.Optional[typing.List[StageInstance]] = [StageInstance.create(client, x) for x in resp.get("stage_instances", [])]
        self.stickers: typing.Optional[typing.List[Sticker]] = [Sticker.create(client, x) for x in resp.get("stickers", [])]

        self.cache = client.cache.get_guild_container(self.id) if client.has_cache else None

    def icon_url(self, *, extension="webp", size=1024) -> typing.Optional[str]:
        if self.icon:
            return cdn_url("icons/{guild_id}", image_hash=self.icon, extension=extension, size=size, guild_id=self.id)

    def splash_url(self, *, extension="webp", size=1024) -> typing.Optional[str]:
        if self.splash:
            return cdn_url("splashes/{guild_id}", image_hash=self.splash, extension=extension, size=size, guild_id=self.id)

    def discovery_splash_url(self, *, extension="webp", size=1024) -> typing.Optional[str]:
        if self.discovery_splash:
            return cdn_url("discovery-splashes/{guild_id}", image_hash=self.discovery_splash, extension=extension, size=size, guild_id=self.id)

    def banner_url(self, *, extension="webp", size=1024) -> typing.Optional[str]:
        if self.banner:
            return cdn_url("banners/{guild_id}", image_hash=self.banner, extension=extension, size=size, guild_id=self.id)

    def request_preview(self) -> "GuildPreview.RESPONSE":
        return self.client.request_guild_preview(self)

    def delete(self):
        return self.client.delete_guild(self)

    def modify(self, **kwargs):
        return self.client.modify_guild(self, **kwargs)

    @property
    def edit(self):
        return self.modify

    def request_channels(self) -> typing.Union[typing.List["Channel"], typing.Awaitable[typing.List["Channel"]]]:
        return self.client.request_guild_channels(self)

    def create_channel(self, name: str, **kwargs) -> "Channel.RESPONSE":
        return self.client.create_guild_channel(self, name, **kwargs)

    def modify_channel_positions(self, *params: dict, reason: str = None):
        return self.client.modify_guild_channel_positions(self, *params, reason=reason)

    def list_active_threads(self) -> typing.Union[typing.List["Channel"], typing.Awaitable[typing.List["Channel"]]]:
        return self.client.list_active_threads_as_guild(self)

    def request_member(self, user: User.TYPING) -> "GuildMember.RESPONSE":
        return self.client.request_guild_member(self, user)

    def list_members(self, limit: int = None, after: str = None) -> typing.Union[typing.List["GuildMember"], typing.Awaitable[typing.List["GuildMember"]]]:
        return self.client.list_guild_members(self, limit, after)

    def remove_guild_member(self, user: User.TYPING):
        return self.client.remove_guild_member(self, user)

    @property
    def kick(self):
        return self.remove_guild_member

    def create_ban(self, user: User.TYPING, *, delete_message_days: int = None, reason: str = None):
        return self.client.create_guild_ban(self, user, delete_message_days=delete_message_days, reason=reason)

    @property
    def ban(self):
        return self.create_ban

    def remove_ban(self, user: User.TYPING, *, reason: str = None):
        return self.client.remove_guild_ban(self, user, reason=reason)

    @property
    def unban(self):
        return self.remove_ban

    def request_roles(self) -> typing.List[Role]:
        return self.client.request_guild_roles(self)

    def create_role(self,
                    *,
                    name: str = None,
                    permissions: typing.Union[int, str, PermissionFlags] = None,
                    color: int = None,
                    hoist: bool = None,
                    mentionable: bool = None,
                    reason: str = None) -> Role:
        kwargs = {"name": name,
                  "permissions": permissions,
                  "color": color,
                  "hoist": hoist,
                  "mentionable": mentionable,
                  "reason": reason}
        return self.client.create_guild_role(self, **kwargs)

    def modify_role_positions(self, *params: dict, reason: str = None):
        return self.client.modify_guild_role_positions(self, *params, reason=reason)

    def modify_role(self,
                    role: Role.TYPING,
                    *,
                    name: str = EmptyObject,
                    permissions: typing.Union[int, str, PermissionFlags] = EmptyObject,
                    color: int = EmptyObject,
                    hoist: bool = EmptyObject,
                    mentionable: bool = EmptyObject,
                    reason: str = None):
        kwargs = {"role": role,
                  "name": name,
                  "permissions": permissions,
                  "color": color,
                  "hoist": hoist,
                  "mentionable": mentionable,
                  "reason": reason}
        return self.client.modify_guild_role(self, **kwargs)

    def delete_role(self, role: Role.TYPING, *, reason: str = None):
        return self.client.delete_guild_role(self, role, reason=reason)

    def request_prune_count(self, *, days: int = None, include_roles: typing.List[Role.TYPING] = None):
        return self.client.request_guild_prune_count(self, days=days, include_roles=include_roles)

    def begin_prune(self,
                    *,
                    days: int = 7,
                    compute_prune_count: bool = True,
                    include_roles: typing.List[Role.TYPING] = None,
                    reason: str = None):
        return self.client.begin_guild_prune(self, days=days, compute_prune_count=compute_prune_count, include_roles=include_roles, reason=reason)

    @property
    def prune(self):
        return self.begin_prune

    def request_voice_regions(self):
        return self.client.request_guild_voice_regions(self)

    def request_invites(self):
        return self.client.request_guild_invites(self)

    def request_integrations(self):
        return self.client.request_guild_integrations(self)

    def delete_integration(self, integration: "Integration.TYPING", *, reason: str = None):
        return self.client.delete_guild_integration(self, integration, reason=reason)

    def request_widget_settings(self):
        return self.client.request_guild_widget_settings(self)

    def modify_widget(self, *, enabled: bool = None, channel: "Channel.TYPING" = EmptyObject, reason: str = None):
        return self.client.modify_guild_widget(self, enabled=enabled, channel=channel, reason=reason)

    def request_widget(self):
        return self.client.request_guild_widget(self)

    def request_vanity_url(self):
        return self.client.request_guild_vanity_url(self)

    def request_widget_image(self, style: str = None):
        return self.client.request_guild_widget_image(self, style)

    def request_welcome_screen(self):
        return self.client.request_guild_welcome_screen(self)

    def modify_guild_welcome_screen(self,
                                    *,
                                    enabled: bool = EmptyObject,
                                    welcome_channels: typing.List[typing.Union["WelcomeScreenChannel", dict]] = EmptyObject,
                                    description: str = EmptyObject,
                                    reason: str = None):
        return self.client.modify_guild_welcome_screen(self, enabled=enabled, welcome_channels=welcome_channels, description=description, reason=reason)

    def modify_user_voice_state(self,
                                channel: "Channel.TYPING",
                                user: User.TYPING = "@me",
                                *,
                                suppress: bool = None,
                                request_to_speak_timestamp: typing.Union[datetime.datetime, str] = None):
        return self.client.modify_user_voice_state(self, channel, user, suppress=suppress, request_to_speak_timestamp=request_to_speak_timestamp)

    def leave(self):
        return self.client.leave_guild(self)

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


class NSFWLevel(TypeBase):
    DEFAULT = 0
    EXPLICIT = 1
    SAFE = 2
    AGE_RESTRICTED = 3


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
    RESPONSE = typing.Union["GuildPreview", typing.Awaitable["GuildPreview"]]

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
    RESPONSE = typing.Union["GuildWidget", typing.Awaitable["GuildWidget"]]
    RESPONSE_AS_LIST = typing.Union[typing.List["GuildWidget"], typing.Awaitable[typing.List["GuildWidget"]]]

    def __init__(self, resp):
        self.enabled = resp["enabled"]
        self.channel_id = Snowflake.optional(resp["channel_id"])


class GuildMember:
    TYPING = typing.Union[int, str, Snowflake, "GuildMember"]
    RESPONSE = typing.Union["GuildMember", typing.Awaitable["GuildMember"]]
    RESPONSE_AS_LIST = typing.Union[typing.List["GuildMember"], typing.Awaitable[typing.List["GuildMember"]]]

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

    def remove(self):
        return self.client.remove_guild_member(self.guild_id, self)

    @property
    def kick(self):
        return self.remove

    def ban(self, *, delete_message_days: int = None, reason: str = None):
        return self.client.create_guild_ban(self.guild_id, self, delete_message_days=delete_message_days, reason=reason)

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


class Integration:
    TYPING = typing.Union[int, str, Snowflake, "Integration"]
    RESPONSE = typing.Union["Integration", typing.Awaitable["Integration"]]
    RESPONSE_AS_LIST = typing.Union[typing.List["Integration"], typing.Awaitable[typing.List["Integration"]]]

    def __init__(self, client, resp):
        self.id = Snowflake(resp["id"])
        self.name = resp["name"]
        self.type = resp["type"]
        self.enabled = resp["enabled"]
        self.syncing = resp.get("syncing")
        self.role_id = Snowflake.optional(resp.get("role_id"))
        self.enable_emoticons = resp.get("enable_emoticons")
        self.__expire_behavior = resp.get("expire_behavior")
        self.expire_behavior = IntegrationExpireBehaviors(int(self.__expire_behavior)) if self.__expire_behavior else self.__expire_behavior
        self.expire_grace_period = resp.get("expire_grace_period")
        self.__user = resp.get("user")
        self.user = User.create(client, self.__user) if self.__user else self.__user
        self.account = IntegrationAccount(resp["account"])
        self.__synced_at = resp.get("synced_at")
        self.synced_at = datetime.datetime.fromisoformat(self.__synced_at) if self.__synced_at else self.__synced_at
        self.subscriber_count = resp.get("subscriber_count")
        self.revoked = resp.get("revoked")
        self.__application = resp.get("application")
        self.application = IntegrationApplication(client, self.__application) if self.__application else self.__application

    def __int__(self):
        return int(self.id)


class IntegrationExpireBehaviors(TypeBase):
    REMOVE_ROLE = 0
    KICK = 1


class IntegrationAccount:
    def __init__(self, resp):
        self.id = resp["id"]
        self.name = resp["name"]


class IntegrationApplication:
    def __init__(self, client, resp):
        self.id = Snowflake(resp["id"])
        self.name = resp["name"]
        self.icon = resp["icon"]
        self.description = resp["description"]
        self.summary = resp["summary"]
        self.__bot = resp.get("bot")
        self.bot = User.create(client, self.__bot) if self.__bot else self.__bot

    def icon_url(self, *, extension="webp", size=1024):
        return cdn_url("app-icons/{application_id}", image_hash=self.icon, extension=extension, size=size, application_id=self.id)


class Ban:
    RESPONSE = typing.Union["Ban", typing.Awaitable["Ban"]]
    RESPONSE_AS_LIST = typing.Union[typing.List["Ban"], typing.Awaitable[typing.List["Ban"]]]

    def __init__(self, client, resp):
        self.reason = resp["reason"]
        self.user = User.create(client, resp["user"])


class WelcomeScreen:
    RESPONSE = typing.Union["WelcomeScreen", typing.Awaitable["WelcomeScreen"]]
    RESPONSE_AS_LIST = typing.Union[typing.List["WelcomeScreen"], typing.Awaitable[typing.List["WelcomeScreen"]]]

    def __init__(self, resp):
        self.description = resp["description"]
        self.welcome_channels = [WelcomeScreenChannel(x) for x in resp["welcome_channels"]]

    def to_dict(self):
        return {"description": self.description, "welcome_channels": [x.to_dict() for x in self.welcome_channels]}


class WelcomeScreenChannel:
    def __init__(self, resp):
        self.channel_id = Snowflake(resp["channel_id"])
        self.description = resp["description"]
        self.emoji_id = Snowflake.optional(resp["emoji_id"])
        self.emoji_name = resp["emoji_name"]

    def to_dict(self):
        return {"channel_id": str(self.channel_id), "description": self.description, "emoji_id": str(self.emoji_id), "emoji_name": self.emoji_name}
