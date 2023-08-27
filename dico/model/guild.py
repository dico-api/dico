import datetime
import typing

from ..base.http import EmptyObject
from ..base.model import AbstractObject, DiscordObjectBase, FlagBase, TypeBase
from ..utils import cdn_url
from .emoji import Emoji
from .extras import BYTES_RESPONSE
from .guild_scheduled_event import GuildScheduledEvent
from .permission import PermissionFlags, Role
from .snowflake import Snowflake
from .stage import StageInstance
from .sticker import Sticker
from .user import User

if typing.TYPE_CHECKING:
    from ..api import APIClient
    from ..cache import GuildCacheContainer
    from .channel import Channel
    from .invite import Invite
    from .voice import VoiceRegion


class Guild(DiscordObjectBase):
    TYPING = typing.Union[int, str, Snowflake, "Guild"]
    RESPONSE = typing.Union["Guild", typing.Awaitable["Guild"]]
    RESPONSE_AS_LIST = typing.Union[
        typing.List["Guild"], typing.Awaitable[typing.List["Guild"]]
    ]
    _cache_type = "guild"

    def __init__(self, client: "APIClient", resp: dict):
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
        self.afk_channel_id: typing.Optional[Snowflake] = Snowflake.optional(
            resp["afk_channel_id"]
        )
        self.afk_timeout: int = resp["afk_timeout"]
        self.widget_enabled: typing.Optional[bool] = resp.get("widget_enabled")
        self.widget_channel_id: typing.Optional[Snowflake] = Snowflake.optional(
            resp.get("widget_channel_id")
        )
        self.verification_level: "VerificationLevel" = VerificationLevel(
            resp["verification_level"]
        )
        self.default_message_notifications: "DefaultMessageNotificationLevel" = (
            DefaultMessageNotificationLevel(resp["default_message_notifications"])
        )
        self.explicit_content_filter: "ExplicitContentFilterLevel" = (
            ExplicitContentFilterLevel(resp["explicit_content_filter"])
        )
        self.roles: typing.List[Role] = [
            Role.create(client, x, guild_id=self.id) for x in resp["roles"]
        ]
        self.emojis: typing.List[Emoji] = [
            Emoji(self.client, x) for x in resp["emojis"]
        ]
        self.features: typing.List[str] = resp["features"]
        self.mfa_level: "MFALevel" = MFALevel(resp["mfa_level"])
        self.application_id: typing.Optional[Snowflake] = Snowflake.optional(
            resp["application_id"]
        )
        self.system_channel_id: typing.Optional[Snowflake] = Snowflake.optional(
            resp["system_channel_id"]
        )
        self.system_channel_flags: SystemChannelFlags = SystemChannelFlags.from_value(
            resp["system_channel_flags"]
        )
        self.rules_channel_id: typing.Optional[Snowflake] = Snowflake.optional(
            resp["rules_channel_id"]
        )
        self.__joined_at = resp.get("joined_at")
        self.joined_at: typing.Optional[datetime.datetime] = (
            datetime.datetime.fromisoformat(self.__joined_at)
            if self.__joined_at
            else self.__joined_at
        )
        self.large: typing.Optional[bool] = resp.get("large")
        self.unavailable: typing.Optional[bool] = resp.get("unavailable")
        self.member_count: typing.Optional[int] = resp.get("member_count")
        self.voice_states: typing.Optional[typing.List[VoiceState]] = [
            VoiceState.create(client, x) for x in resp.get("voice_states", [])
        ]
        self.members: typing.Optional[typing.List["GuildMember"]] = [
            GuildMember.create(self.client, x, guild_id=self.id)
            for x in resp.get("members", [])
        ]
        self.channels: typing.Optional[typing.List[Channel]] = [
            Channel.create(client, x, guild_id=self.id)
            for x in resp.get("channels", [])
        ]
        self.threads: typing.Optional[typing.List[Channel]] = [
            Channel.create(client, x, guild_id=self.id, ensure_cache_type="channel")
            for x in resp.get("threads", [])
        ]
        self.presences: typing.Optional[typing.List[PresenceUpdate]] = [
            PresenceUpdate.create(client, x) for x in resp.get("presences", [])
        ]
        self.max_presences: typing.Optional[int] = resp.get("max_presences")
        self.max_members: typing.Optional[int] = resp.get("max_members")
        self.vanity_url_code: typing.Optional[str] = resp["vanity_url_code"]
        self.description: typing.Optional[str] = resp["description"]
        self.banner: typing.Optional[str] = resp["banner"]
        self.premium_tier: "PremiumTier" = PremiumTier(resp["premium_tier"])
        self.premium_subscription_count: int = resp.get("premium_subscription_count")
        self.preferred_locale: str = resp["preferred_locale"]
        self.public_updates_channel_id: typing.Optional[Snowflake] = Snowflake.optional(
            resp["public_updates_channel_id"]
        )
        self.max_video_channel_users: typing.Optional[int] = resp.get(
            "max_video_channel_users"
        )
        self.approximate_member_count: typing.Optional[int] = resp.get(
            "approximate_member_count"
        )
        self.approximate_presence_count: typing.Optional[int] = resp.get(
            "approximate_presence_count"
        )
        self.__welcome_screen = resp.get("welcome_screen")
        self.welcome_screen: typing.Optional["WelcomeScreen"] = (
            WelcomeScreen(self.__welcome_screen)
            if self.__welcome_screen
            else self.__welcome_screen
        )
        self.nsfw_level: "NSFWLevel" = NSFWLevel(resp["nsfw_level"])
        self.stage_instances: typing.Optional[typing.List[StageInstance]] = [
            StageInstance.create(client, x) for x in resp.get("stage_instances", [])
        ]
        self.stickers: typing.Optional[typing.List[Sticker]] = [
            Sticker.create(client, x) for x in resp.get("stickers", [])
        ]
        self.__guild_scheduled_events = resp.get("guild_scheduled_events", [])
        self._guild_scheduled_events: typing.List[GuildScheduledEvent] = [
            GuildScheduledEvent.create(self.client, x)
            for x in self.__guild_scheduled_events
        ]
        self.premium_progress_bar_enabled: bool = resp["premium_progress_bar_enabled"]
        self.safety_alerts_channel_id: typing.Optional[Snowflake] = Snowflake.optional(
            resp.get("safety_alerts_channel_id")
        )

    def icon_url(
        self, *, extension: str = "webp", size: int = 1024
    ) -> typing.Optional[str]:
        if self.icon:
            return cdn_url(
                "icons/{guild_id}",
                image_hash=self.icon,
                extension=extension,
                size=size,
                guild_id=self.id,
            )

    def splash_url(
        self, *, extension: str = "webp", size: int = 1024
    ) -> typing.Optional[str]:
        if self.splash:
            return cdn_url(
                "splashes/{guild_id}",
                image_hash=self.splash,
                extension=extension,
                size=size,
                guild_id=self.id,
            )

    def discovery_splash_url(
        self, *, extension: str = "webp", size: int = 1024
    ) -> typing.Optional[str]:
        if self.discovery_splash:
            return cdn_url(
                "discovery-splashes/{guild_id}",
                image_hash=self.discovery_splash,
                extension=extension,
                size=size,
                guild_id=self.id,
            )

    def banner_url(
        self, *, extension: str = "webp", size: int = 1024
    ) -> typing.Optional[str]:
        if self.banner:
            return cdn_url(
                "banners/{guild_id}",
                image_hash=self.banner,
                extension=extension,
                size=size,
                guild_id=self.id,
            )

    def request_preview(self) -> "GuildPreview.RESPONSE":
        return self.client.request_guild_preview(self)

    def delete(self):
        return self.client.delete_guild(self)

    def modify(self, **kwargs) -> "Guild.RESPONSE":
        return self.client.modify_guild(self, **kwargs)

    @property
    def edit(self):
        return self.modify

    def request_channels(self) -> "Channel.RESPONSE_AS_LIST":
        return self.client.request_guild_channels(self)

    def create_channel(self, name: str, **kwargs) -> "Channel.RESPONSE":
        return self.client.create_guild_channel(self, name, **kwargs)

    def modify_channel_positions(self, *params: dict, reason: str = None):
        return self.client.modify_guild_channel_positions(self, *params, reason=reason)

    def list_active_threads(self) -> "Channel.RESPONSE_AS_LIST":
        return self.client.list_active_threads(self)

    def request_member(self, user: User.TYPING) -> "GuildMember.RESPONSE":
        return self.client.request_guild_member(self, user)

    def list_members(
        self, limit: int = None, after: str = None
    ) -> "GuildMember.RESPONSE_AS_LIST":
        return self.client.list_guild_members(self, limit, after)

    def remove_guild_member(self, user: User.TYPING):
        return self.client.remove_guild_member(self, user)

    @property
    def kick(self):
        return self.remove_guild_member

    def create_ban(
        self, user: User.TYPING, *, delete_message_days: int = None, reason: str = None
    ):
        return self.client.create_guild_ban(
            self, user, delete_message_days=delete_message_days, reason=reason
        )

    @property
    def ban(self):
        return self.create_ban

    def remove_ban(self, user: User.TYPING, *, reason: str = None):
        return self.client.remove_guild_ban(self, user, reason=reason)

    @property
    def unban(self):
        return self.remove_ban

    def request_roles(self) -> Role.RESPONSE_AS_LIST:
        return self.client.request_guild_roles(self)

    def create_role(
        self,
        *,
        name: str = None,
        permissions: typing.Union[int, str, PermissionFlags] = None,
        color: int = None,
        hoist: bool = None,
        mentionable: bool = None,
        reason: str = None,
    ) -> Role.RESPONSE:
        kwargs = {
            "name": name,
            "permissions": permissions,
            "color": color,
            "hoist": hoist,
            "mentionable": mentionable,
            "reason": reason,
        }
        return self.client.create_guild_role(self, **kwargs)

    def modify_role_positions(
        self, *params: dict, reason: str = None
    ) -> Role.RESPONSE_AS_LIST:
        return self.client.modify_guild_role_positions(self, *params, reason=reason)

    def modify_role(
        self,
        role: Role.TYPING,
        *,
        name: str = EmptyObject,
        permissions: typing.Union[int, str, PermissionFlags] = EmptyObject,
        color: int = EmptyObject,
        hoist: bool = EmptyObject,
        mentionable: bool = EmptyObject,
        reason: str = None,
    ) -> Role.RESPONSE:
        kwargs = {
            "role": role,
            "name": name,
            "permissions": permissions,
            "color": color,
            "hoist": hoist,
            "mentionable": mentionable,
            "reason": reason,
        }
        return self.client.modify_guild_role(self, **kwargs)

    def delete_role(self, role: Role.TYPING, *, reason: str = None):
        return self.client.delete_guild_role(self, role, reason=reason)

    def request_prune_count(
        self, *, days: int = None, include_roles: typing.List[Role.TYPING] = None
    ) -> AbstractObject.RESPONSE:
        return self.client.request_guild_prune_count(
            self, days=days, include_roles=include_roles
        )

    def begin_prune(
        self,
        *,
        days: int = 7,
        compute_prune_count: bool = True,
        include_roles: typing.List[Role.TYPING] = None,
        reason: str = None,
    ) -> AbstractObject.RESPONSE:
        return self.client.begin_guild_prune(
            self,
            days=days,
            compute_prune_count=compute_prune_count,
            include_roles=include_roles,
            reason=reason,
        )

    @property
    def prune(self):
        return self.begin_prune

    def request_voice_regions(self) -> "VoiceRegion.RESPONSE_AS_LIST":
        return self.client.request_guild_voice_regions(self)

    def request_invites(self) -> "Invite.RESPONSE_AS_LIST":
        return self.client.request_guild_invites(self)

    def request_integrations(self) -> "Integration.RESPONSE_AS_LIST":
        return self.client.request_guild_integrations(self)

    def delete_integration(
        self, integration: "Integration.TYPING", *, reason: str = None
    ):
        return self.client.delete_guild_integration(self, integration, reason=reason)

    def request_widget_settings(self) -> "GuildWidgetSettings.RESPONSE":
        return self.client.request_guild_widget_settings(self)

    def modify_widget(
        self,
        *,
        enabled: bool = None,
        channel: "Channel.TYPING" = EmptyObject,
        reason: str = None,
    ) -> "GuildWidgetSettings.RESPONSE":
        return self.client.modify_guild_widget(
            self, enabled=enabled, channel=channel, reason=reason
        )

    def request_widget(self) -> "GuildWidget.RESPONSE":
        return self.client.request_guild_widget(self)

    def request_vanity_url(self) -> AbstractObject.RESPONSE:
        return self.client.request_guild_vanity_url(self)

    def request_widget_image(self, style: str = None) -> BYTES_RESPONSE:
        return self.client.request_guild_widget_image(self, style)

    def request_welcome_screen(self) -> "WelcomeScreen.RESPONSE":
        return self.client.request_guild_welcome_screen(self)

    def modify_guild_welcome_screen(
        self,
        *,
        enabled: bool = EmptyObject,
        welcome_channels: typing.List[
            typing.Union["WelcomeScreenChannel", dict]
        ] = EmptyObject,
        description: str = EmptyObject,
        reason: str = None,
    ) -> "WelcomeScreen.RESPONSE":
        return self.client.modify_guild_welcome_screen(
            self,
            enabled=enabled,
            welcome_channels=welcome_channels,
            description=description,
            reason=reason,
        )

    def modify_user_voice_state(
        self,
        channel: "Channel.TYPING",
        user: User.TYPING = "@me",
        *,
        suppress: bool = None,
        request_to_speak_timestamp: typing.Union[datetime.datetime, str] = None,
    ):
        return self.client.modify_user_voice_state(
            self,
            channel,
            user,
            suppress=suppress,
            request_to_speak_timestamp=request_to_speak_timestamp,
        )

    def leave(self):
        return self.client.leave_guild(self)

    @property
    def guild_scheduled_events(
        self,
    ) -> typing.Optional[typing.List[GuildScheduledEvent]]:
        if self.client.has_cache:
            events = [
                x
                for x in self.client.cache.get_storage(GuildScheduledEvent._cache_type)
                if x.guild_id == self.id
            ]
            if events:
                return events
        return self._guild_scheduled_events

    @property
    def cache(self) -> typing.Optional["GuildCacheContainer"]:
        if self.client.has_cache:
            return self.client.cache.get_guild_container(self.id)

    @property
    def get(self) -> typing.Optional["GuildCacheContainer.get"]:
        """Alias of ``Guild.cache.get``."""
        if self.cache:
            return self.cache.get

    def get_owner(self) -> typing.Optional[typing.Union["GuildMember", User]]:
        if self.cache:
            return self.get(self.owner_id, "member") or self.get(self.owner_id, "user")

    def __repr__(self):
        return f"<{self.__class__.__name__} id={self.id} name={self.name}>"


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
    SUPPRESS_JOIN_NOTIFICATION_REPLIES = 1 << 3
    SUPPRESS_ROLE_SUBSCRIPTION_PURCHASE_NOTIFICATIONS = 1 << 4
    SUPPRESS_ROLE_SUBSCRIPTION_PURCHASE_NOTIFICATION_REPLIES = 1 << 5


class GuildPreview:
    RESPONSE = typing.Union["GuildPreview", typing.Awaitable["GuildPreview"]]

    def __init__(self, client: "APIClient", resp: dict):
        self.id: Snowflake = Snowflake(resp["id"])
        self.name: str = resp["name"]
        self.icon: typing.Optional[str] = resp["icon"]
        self.splash: typing.Optional[str] = resp["splash"]
        self.discovery_splash: typing.Optional[str] = resp["discovery_splash"]
        self.emojis: typing.List[Emoji] = [Emoji(client, x) for x in resp["emojis"]]
        self.features: typing.List[str] = resp["features"]
        self.approximate_member_count: int = resp["approximate_member_count"]
        self.approximate_presence_count: int = resp["approximate_presence_count"]
        self.description: typing.Optional[str] = resp["description"]
        self.stickers: typing.List[Sticker] = [
            Sticker(client, x) for x in resp["stickers"]
        ]


class GuildWidgetSettings:
    RESPONSE = typing.Union[
        "GuildWidgetSettings", typing.Awaitable["GuildWidgetSettings"]
    ]
    RESPONSE_AS_LIST = typing.Union[
        typing.List["GuildWidgetSettings"],
        typing.Awaitable[typing.List["GuildWidgetSettings"]],
    ]

    def __init__(self, resp: dict):
        self.enabled: bool = resp["enabled"]
        self.channel_id: typing.Optional[Snowflake] = Snowflake.optional(
            resp["channel_id"]
        )


class GuildWidget:
    RESPONSE = typing.Union["GuildWidget", typing.Awaitable["GuildWidget"]]
    RESPONSE_AS_LIST = typing.Union[
        typing.List["GuildWidget"], typing.Awaitable[typing.List["GuildWidget"]]
    ]

    def __init__(self, client: "APIClient", resp: dict):
        from .channel import Channel  # Prevent circular import.

        self.id: Snowflake = Snowflake(resp["id"])
        self.name: str = resp["name"]
        self.instant_invite: typing.Optional[str] = resp["instant_invite"]
        self.channels: typing.List[Channel] = [
            Channel.create(client, x) for x in resp["channels"]
        ]
        self.members: typing.List[User] = [
            User.create(client, x) for x in resp["members"]
        ]
        self.presence_count: int = resp["presence_count"]


class GuildMember:
    TYPING = typing.Union[int, str, Snowflake, "GuildMember"]
    RESPONSE = typing.Union["GuildMember", typing.Awaitable["GuildMember"]]
    RESPONSE_AS_LIST = typing.Union[
        typing.List["GuildMember"], typing.Awaitable[typing.List["GuildMember"]]
    ]

    def __init__(
        self,
        client: "APIClient",
        resp: dict,
        *,
        user: User = None,
        guild_id: Snowflake = None,
    ):
        self.raw: dict = resp
        self.client: "APIClient" = client
        self.user = user
        self.__user = resp.get("user")
        self.user: typing.Optional[User] = (
            User.create(client, self.__user)
            if self.__user and not self.user
            else self.user
            if self.user
            else self.__user
        )
        self.nick: typing.Optional[str] = resp.get("nick")
        self.avatar: typing.Optional[str] = resp.get("avatar")
        self.roles: typing.Optional[typing.List[Role]] = (
            [client.get(x, "role") for x in resp["roles"]] if client.has_cache else []
        )
        self.role_ids: typing.List[Snowflake] = [Snowflake(x) for x in resp["roles"]]
        self.joined_at: datetime.datetime = datetime.datetime.fromisoformat(
            resp["joined_at"]
        )
        self.__premium_since = resp.get("premium_since")
        self.premium_since: datetime.datetime = (
            datetime.datetime.fromisoformat(self.__premium_since)
            if self.__premium_since
            else self.__premium_since
        )
        self.deaf: typing.Optional[bool] = resp.get("deaf", False)
        self.mute: typing.Optional[bool] = resp.get("mute", False)
        self.pending: typing.Optional[bool] = resp.get("pending", False)
        self.__permissions = resp.get("permissions")
        self.__communication_disabled_until = resp.get("communication_disabled_until")
        self.communication_disabled_until: typing.Optional[datetime.datetime] = (
            datetime.datetime.fromisoformat(self.__communication_disabled_until)
            if self.__communication_disabled_until
            else self.__communication_disabled_until
        )
        self.guild_id: typing.Optional[Snowflake] = Snowflake.optional(
            resp.get("guild_id")
        ) or Snowflake.ensure_snowflake(guild_id)

    def __str__(self) -> str:
        return self.nick or (self.user.username if self.user else None)

    def __int__(self) -> int:
        if self.user:
            return int(self.user.id)

    def avatar_url(
        self, *, extension: str = "webp", size: int = 1024
    ) -> typing.Optional[str]:
        if self.avatar:
            return cdn_url(
                "guilds/{guild_id}/users/{user_id}/avatars",
                image_hash=self.avatar,
                extension=extension,
                size=size,
                guild_id=self.guild_id,
                user_id=self.id,
            )
        elif self.user:
            return self.user.avatar_url(extension=extension, size=size)

    def remove(self):
        return self.client.remove_guild_member(self.guild_id, self)

    @property
    def kick(self):
        return self.remove

    def ban(self, *, delete_message_days: int = None, reason: str = None):
        return self.client.create_guild_ban(
            self.guild_id, self, delete_message_days=delete_message_days, reason=reason
        )

    @property
    def id(self) -> typing.Optional[Snowflake]:
        if self.user:
            return self.user.id

    @property
    def mention(self) -> str:
        if self.user:
            return f"<@{self.user.id}>"

    @property
    def permissions(self) -> typing.Optional[PermissionFlags]:
        if self.__permissions:
            return PermissionFlags.from_value(int(self.__permissions))
        elif self.roles:
            value = 0
            for x in self.roles:
                if isinstance(x, Role):
                    value |= x.permissions.value
                else:
                    return None
            return PermissionFlags.from_value(value)
        else:
            return PermissionFlags.from_value(0)

    @classmethod
    def create(
        cls,
        client: "APIClient",
        resp: dict,
        *,
        user: User = None,
        guild_id: Snowflake.TYPING = None,
        cache: bool = True,
    ):
        if (
            cache
            and client.has_cache
            and (guild_id or resp.get("guild_id"))
            and (user or resp.get("user"))
        ):
            _guild_id = guild_id or resp.get("guild_id")
            _user_id = user.id if isinstance(user, User) else resp["user"]["id"]
            maybe_exist = (
                client.cache.get_guild_container(_guild_id)
                .get_storage("member")
                .get(_user_id)
            )
            if maybe_exist:
                orig = maybe_exist.raw
                for k, v in resp.items():
                    if orig.get(k) != v:
                        orig[k] = v
                maybe_exist.__init__(client, orig, user=user, guild_id=guild_id)
                return maybe_exist
        ret = cls(client, resp, user=user, guild_id=guild_id)
        if cache and client.has_cache and ret.guild_id and ret.user:
            client.cache.get_guild_container(ret.guild_id).add(
                ret.user.id, "member", ret
            )
        return ret


class Integration:
    TYPING = typing.Union[int, str, Snowflake, "Integration"]
    RESPONSE = typing.Union["Integration", typing.Awaitable["Integration"]]
    RESPONSE_AS_LIST = typing.Union[
        typing.List["Integration"], typing.Awaitable[typing.List["Integration"]]
    ]

    def __init__(self, client: "APIClient", resp: dict):
        self.client: "APIClient" = client
        self.raw: dict = resp
        self.id: Snowflake = Snowflake(resp["id"])
        self.name: str = resp["name"]
        self.type: str = resp["type"]
        self.enabled: typing.Optional[bool] = resp.get("enabled")
        self.syncing: typing.Optional[bool] = resp.get("syncing")
        self.role_id: typing.Optional[Snowflake] = Snowflake.optional(
            resp.get("role_id")
        )
        self.enable_emoticons: typing.Optional[bool] = resp.get("enable_emoticons")
        self.__expire_behavior = resp.get("expire_behavior")
        self.expire_behavior: typing.Optional[IntegrationExpireBehaviors] = (
            IntegrationExpireBehaviors(int(self.__expire_behavior))
            if self.__expire_behavior
            else self.__expire_behavior
        )
        self.expire_grace_period: typing.Optional[int] = resp.get("expire_grace_period")
        self.__user = resp.get("user")
        self.user: typing.Optional[User] = (
            User.create(client, self.__user) if self.__user else self.__user
        )
        self.account: IntegrationAccount = IntegrationAccount(resp["account"])
        self.__synced_at = resp.get("synced_at")
        self.synced_at: typing.Optional[datetime.datetime] = (
            datetime.datetime.fromisoformat(self.__synced_at)
            if self.__synced_at
            else self.__synced_at
        )
        self.subscriber_count: typing.Optional[int] = resp.get("subscriber_count")
        self.revoked: typing.Optional[bool] = resp.get("revoked")
        self.__application = resp.get("application")
        self.application: typing.Optional[IntegrationApplication] = (
            IntegrationApplication(client, self.__application)
            if self.__application
            else self.__application
        )
        self.scopes: typing.Optional[str] = resp.get("scopes")

    def __int__(self) -> int:
        return int(self.id)

    @property
    def role(self) -> typing.Optional[Role]:
        if self.client.has_cache:
            return self.client.cache.get(self.role_id, "role")


class IntegrationExpireBehaviors(TypeBase):
    REMOVE_ROLE = 0
    KICK = 1


class IntegrationAccount:
    def __init__(self, resp: dict):
        self.id: str = resp["id"]
        self.name: str = resp["name"]


class IntegrationApplication:
    def __init__(self, client: "APIClient", resp: dict):
        self.id: Snowflake = Snowflake(resp["id"])
        self.name: str = resp["name"]
        self.icon: typing.Optional[str] = resp["icon"]
        self.description: str = resp["description"]
        self.summary: str = resp["summary"]
        self.__bot = resp.get("bot")
        self.bot: typing.Optional[User] = (
            User.create(client, self.__bot) if self.__bot else self.__bot
        )

    def icon_url(
        self, *, extension: str = "webp", size: int = 1024
    ) -> typing.Optional[str]:
        return cdn_url(
            "app-icons/{application_id}",
            image_hash=self.icon,
            extension=extension,
            size=size,
            application_id=self.id,
        )


class Ban:
    RESPONSE = typing.Union["Ban", typing.Awaitable["Ban"]]
    RESPONSE_AS_LIST = typing.Union[
        typing.List["Ban"], typing.Awaitable[typing.List["Ban"]]
    ]

    def __init__(self, client: "APIClient", resp: dict):
        self.reason: typing.Optional[str] = resp["reason"]
        self.user: User = User.create(client, resp["user"])


class WelcomeScreen:
    RESPONSE = typing.Union["WelcomeScreen", typing.Awaitable["WelcomeScreen"]]
    RESPONSE_AS_LIST = typing.Union[
        typing.List["WelcomeScreen"], typing.Awaitable[typing.List["WelcomeScreen"]]
    ]

    def __init__(self, resp: dict):
        self.description: typing.Optional[str] = resp["description"]
        self.welcome_channels: typing.List[WelcomeScreenChannel] = [
            WelcomeScreenChannel(x) for x in resp["welcome_channels"]
        ]

    def to_dict(self):
        return {
            "description": self.description,
            "welcome_channels": [x.to_dict() for x in self.welcome_channels],
        }


class WelcomeScreenChannel:
    def __init__(self, resp: dict):
        self.channel_id: Snowflake = Snowflake(resp["channel_id"])
        self.description: str = resp["description"]
        self.emoji_id: typing.Optional[Snowflake] = Snowflake.optional(resp["emoji_id"])
        self.emoji_name: typing.Optional[str] = resp["emoji_name"]

    def to_dict(self) -> dict:
        return {
            "channel_id": str(self.channel_id),
            "description": self.description,
            "emoji_id": str(self.emoji_id),
            "emoji_name": self.emoji_name,
        }


class Onboarding:
    RESPONSE = typing.Union["Onboarding", typing.Awaitable["Onboarding"]]

    def __init__(self, client: "APIClient", resp: dict):
        self.guild_id: Snowflake = Snowflake(resp["guild_id"])
        self.prompts: typing.List["OnboardingPrompt"] = [
            OnboardingPrompt(client, x) for x in resp["prompts"]
        ]
        self.default_channel_ids: typing.List[Snowflake] = [
            Snowflake(x) for x in resp["default_channel_ids"]
        ]
        self.enabled: bool = resp["enabled"]
        self.mode: "OnboardingMode" = OnboardingMode(resp["mode"])


class OnboardingPrompt:
    def __init__(self, client: "APIClient", resp: dict):
        self.id: Snowflake = Snowflake(resp["id"])
        self.type: "PromptTypes" = PromptTypes(resp["type"])
        self.options: typing.List["PromptOption"] = [
            PromptOption(client, x) for x in resp["options"]
        ]
        self.title: str = resp["title"]
        self.single_select: bool = resp["single_select"]
        self.required: bool = resp["required"]
        self.in_onboarding: bool = resp["in_onboarding"]


class PromptOption:
    def __init__(self, client: "APIClient", resp: dict):
        self.id: Snowflake = Snowflake(resp["id"])
        self.channel_ids: typing.List[Snowflake] = [
            Snowflake(x) for x in resp["channel_ids"]
        ]
        self.role_ids: typing.List[Snowflake] = [Snowflake(x) for x in resp["role_ids"]]
        self.emoji: Emoji = Emoji(client, resp["emoji"])
        self.title: str = resp["title"]
        self.description: typing.Optional[str] = resp["description"]


class OnboardingMode(TypeBase):
    ONBOARDING_DEFAULT = 0
    ONBOARDING_ADVANCED = 1


class PromptTypes(TypeBase):
    MULTIPLE_CHOICE = 0
    DROPDOWN = 1
