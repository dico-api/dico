import inspect
import typing
import pathlib
import datetime

from .emoji import Emoji
from .guild import GuildMember
from .permission import PermissionFlags, Role
from .snowflake import Snowflake
from .sticker import Sticker, StickerItem
from .user import User
from ..base.model import CopyableObject, DiscordObjectBase, TypeBase, FlagBase

if typing.TYPE_CHECKING:
    from .application import Application
    from .guild import Guild
    from .invite import Invite
    from ..api import APIClient


class Channel(DiscordObjectBase):
    TYPING = typing.Union[int, str, Snowflake, "Channel"]
    RESPONSE = typing.Union["Channel", typing.Awaitable["Channel"]]
    RESPONSE_AS_LIST = typing.Union[typing.List["Channel"], typing.Awaitable[typing.List["Channel"]]]
    _cache_type = "channel"

    def __init__(self, client: "APIClient", resp: dict, *, guild_id: Snowflake.TYPING = None):
        super().__init__(client, resp)
        self.type: ChannelTypes = ChannelTypes(resp["type"])
        self.guild_id: Snowflake = Snowflake.optional(resp.get("guild_id")) or Snowflake.ensure_snowflake(guild_id)
        self.position: typing.Optional[int] = resp.get("position")
        self.permission_overwrites: typing.Optional[typing.List[Overwrite]] = [Overwrite.create(x) for x in resp.get("permission_overwrites", [])]
        self.name: typing.Optional[str] = resp.get("name")
        self.topic: typing.Optional[str] = resp.get("topic")
        self.nsfw: typing.Optional[bool] = resp.get("nsfw")
        self.last_message_id: typing.Optional[Snowflake] = Snowflake.optional(resp.get("last_message_id"))
        self.bitrate: typing.Optional[int] = resp.get("bitrate")
        self.user_limit: typing.Optional[int] = resp.get("user_limit")
        self.rate_limit_per_user: typing.Optional[int] = resp.get("rate_limit_per_user")
        self.recipients: typing.Optional[typing.List[User]] = [User.create(client, x) for x in resp.get("recipients", [])]
        self.icon: typing.Optional[str] = resp.get("icon")
        self.owner_id: typing.Optional[Snowflake] = Snowflake.optional(resp.get("owner_id"))
        self.application_id: typing.Optional[Snowflake] = Snowflake.optional(resp.get("application_id"))
        self.parent_id: typing.Optional[Snowflake] = Snowflake.optional(resp.get("parent_id"))
        self.__last_pin_timestamp = resp.get("last_pin_timestamp")
        self.last_pin_timestamp: typing.Optional[datetime.datetime] = datetime.datetime.fromisoformat(self.__last_pin_timestamp) if self.__last_pin_timestamp else self.__last_pin_timestamp
        self.rtc_region: typing.Optional[str] = resp.get("rtc_region")
        self.__video_quality_mode = resp.get("video_quality_mode")
        self.video_quality_mode: typing.Optional[VideoQualityModes] = VideoQualityModes(self.__video_quality_mode) if self.__video_quality_mode else self.__video_quality_mode
        self.message_count: typing.Optional[int] = resp.get("message_count")
        self.member_count: typing.Optional[int] = resp.get("member_count")
        self.thread_metadata: typing.Optional[ThreadMetadata] = ThreadMetadata.optional(self.client, resp.get("thread_metadata"))
        self.member: typing.Optional[ThreadMember] = ThreadMember.optional(self.client, resp.get("member"))
        self.default_auto_archive_duration: typing.Optional[int] = resp.get("default_auto_archive_duration")
        self.__permissions = resp.get("permissions")
        self.permissions: typing.Optional[PermissionFlags] = PermissionFlags.from_value(int(self.__permissions)) if self.__permissions else self.__permissions

        # if self.type.dm and self.

    def __str__(self) -> str:
        return self.name

    def modify(self, **kwargs) -> RESPONSE:
        if self.type.group_dm:
            return self.client.modify_group_dm_channel(self.id, **kwargs)
        elif self.type.dm or self.type.guild_store:
            raise AttributeError("This type of channel is not allowed to modify.")
        elif self.is_thread_channel():
            return self.client.modify_thread_channel(self.id, **kwargs)
        else:
            return self.client.modify_guild_channel(self.id, **kwargs)

    @property
    def edit(self):
        return self.modify

    def delete(self, *, reason: str = None) -> RESPONSE:
        return self.client.delete_channel(self, reason=reason)

    def create_message(self, *args, **kwargs) -> "Message.RESPONSE":
        if not self.is_messageable():
            raise TypeError("You can't send message in this type of channel.")
        return self.client.create_message(self, *args, **kwargs)

    @property
    def send(self):
        return self.create_message

    def bulk_delete_messages(self, *messages: "Message.TYPING", reason: str = None):
        return self.client.bulk_delete_messages(self, *messages, reason=reason)

    def edit_permissions(self, overwrite, *, reason: str = None):
        return self.client.edit_channel_permissions(self, overwrite, reason=reason)

    def request_invites(self) -> "Invite.RESPONSE_AS_LIST":
        return self.client.request_channel_invites(self)

    def create_invite(self, **kwargs) -> "Invite.RESPONSE":
        return self.client.create_channel_invite(self, **kwargs)

    def delete_permissions(self, overwrite, *, reason: str = None):
        return self.client.delete_channel_permission(self, overwrite, reason=reason)

    def follow(self, target_channel: "Channel.TYPING") -> "FollowedChannel.RESPONSE":
        return self.client.follow_news_channel(self, target_channel)

    def trigger_typing_indicator(self):
        return self.client.trigger_typing_indicator(self)

    def request_pinned_messages(self) -> "Message.RESPONSE_AS_LIST":
        return self.client.request_pinned_messages(self)

    def add_recipient(self, user: User.TYPING, access_token: str, nick: str):
        if not self.type.group_dm:
            raise AttributeError("This type of channel is not allowed to add recipient.")
        return self.client.group_dm_add_recipient(self, user, access_token, nick)

    def remove_recipient(self, user: User.TYPING):
        if not self.type.group_dm:
            raise AttributeError("This type of channel is not allowed to remove recipient.")
        return self.client.group_dm_remove_recipient(self, user)

    def start_thread(self, message: "Message.TYPING" = None, *, name: str, auto_archive_duration: int, reason: str = None) -> "Channel.RESPONSE":
        return self.client.start_thread(self, message, name=name, auto_archive_duration=auto_archive_duration, reason=reason)

    def join_thread(self):
        if not self.is_thread_channel():
            raise AttributeError("This type of channel is not allowed to join thread.")
        return self.client.join_thread(self)

    def add_thread_member(self, user: User.TYPING):
        if not self.is_thread_channel():
            raise AttributeError("This type of channel is not allowed to add thread member.")
        return self.client.add_thread_member(self, user)

    def leave_thread(self):
        if not self.is_thread_channel():
            raise AttributeError("This type of channel is not allowed to leave thread.")
        return self.client.leave_thread(self)

    def remove_thread_member(self, user: User.TYPING):
        if not self.is_thread_channel():
            raise AttributeError("This type of channel is not allowed to remove thread member.")
        return self.client.remove_thread_member(self, user)

    def list_thread_members(self) -> "ThreadMember.RESPONSE_AS_LIST":
        if not self.is_thread_channel():
            raise AttributeError("This type of channel is not allowed to list thread members.")
        return self.client.list_thread_members(self)

    def list_active_threads(self) -> "ListThreadsResponse.RESPONSE":
        return self.client.list_active_threads(self)

    def list_public_archived_threads(self, *, before: typing.Union[str, datetime.datetime] = None, limit: int = None) -> "ListThreadsResponse.RESPONSE":
        return self.client.list_public_archived_threads(self, before=before, limit=limit)

    def list_private_archived_threads(self, *, before: typing.Union[str, datetime.datetime] = None, limit: int = None) -> "ListThreadsResponse.RESPONSE":
        return self.client.list_private_archived_threads(self, before=before, limit=limit)

    def list_joined_private_archived_threads(self, *, before: typing.Union[str, datetime.datetime] = None, limit: int = None) -> "ListThreadsResponse.RESPONSE":
        return self.client.list_joined_private_archived_threads(self, before=before, limit=limit)

    def archive(self, locked: bool = False):
        if not self.is_thread_channel():
            raise AttributeError("This type of channel is not allowed to archive.")
        return self.modify(archived=True, locked=locked)

    def to_position_param(self, position: int = None, lock_permissions: bool = None, parent: typing.Union[int, str, Snowflake, "Channel"] = None) -> dict:
        if isinstance(parent, Channel) and not parent.type.guild_category:
            raise TypeError("parent must be category channel.")
        param = {
            "id": str(self.id),
            "position": position,
            "lock_permissions": lock_permissions,
            "parent_id": str(int(parent))
        }
        return param

    @property
    def mention(self) -> str:
        return f"<#{self.id}>"

    @property
    def guild(self) -> typing.Optional["Guild"]:
        if self.guild_id and self.client.has_cache:
            return self.client.cache.get(self.guild_id, "guild")  # noqa

    def is_messageable(self) -> bool:
        if self.is_thread_channel():
            return self.thread_metadata.archived
        return self.type.guild_text or self.type.guild_news or self.type.dm or self.type.group_dm

    def is_thread_channel(self) -> bool:
        return self.type.guild_news_thread or self.type.guild_public_thread or self.type.guild_private_thread

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} id={self.id} name={self.name}>'


class ChannelTypes(TypeBase):
    GUILD_TEXT = 0
    DM = 1
    GUILD_VOICE = 2
    GROUP_DM = 3
    GUILD_CATEGORY = 4
    GUILD_NEWS = 5
    GUILD_STORE = 6
    GUILD_NEWS_THREAD = 10
    GUILD_PUBLIC_THREAD = 11
    GUILD_PRIVATE_THREAD = 12
    GUILD_STAGE_VOICE = 13


class VideoQualityModes(TypeBase):
    AUTO = 1
    FULL = 2


class SendOnlyChannel:
    def __init__(self, client: "APIClient", channel_id: Snowflake.TYPING):
        self.client: "APIClient" = client
        self.id: Snowflake = Snowflake.ensure_snowflake(channel_id)

    def send(self, *args, **kwargs) -> "Message.RESPONSE":
        return self.client.create_message(self.id, *args, **kwargs)

    def __getattr__(self, item):
        return None


class Message(DiscordObjectBase):
    TYPING = typing.Union[int, str, Snowflake, "Message"]
    RESPONSE = typing.Union["Message", typing.Awaitable["Message"]]
    RESPONSE_AS_LIST = typing.Union[typing.List["Message"], typing.Awaitable[typing.List["Message"]]]
    _cache_type = "message"

    def __init__(self,
                 client: "APIClient",
                 resp: dict,
                 *,
                 guild_id: Snowflake.TYPING = None,
                 webhook_token: typing.Optional[str] = None,
                 interaction_token: typing.Optional[str] = None,
                 original_response: typing.Optional[bool] = False):
        from .interactions import MessageInteraction, Component  # Prevent circular import.
        super().__init__(client, resp)
        self.channel_id: Snowflake = Snowflake(resp["channel_id"])
        self.guild_id: typing.Optional[Snowflake] = Snowflake.optional(resp.get("guild_id") or guild_id)
        self.author: User = User.create(client, resp["author"])
        self.__member = resp.get("member")
        self.member: GuildMember = GuildMember.create(self.client, self.__member, user=self.author, guild_id=self.guild_id) if self.__member else self.__member
        self.content: str = resp["content"]
        self.timestamp: datetime.datetime = datetime.datetime.fromisoformat(resp["timestamp"])
        self.__edited_timestamp = resp["edited_timestamp"]
        self.edited_timestamp: typing.Optional[datetime.datetime] = datetime.datetime.fromisoformat(self.__edited_timestamp) if self.__edited_timestamp else self.__edited_timestamp
        self.tts: bool = resp["tts"]
        self.mention_everyone: bool = resp["mention_everyone"]
        self.mentions: typing.List[typing.Union[User, GuildMember]] = [GuildMember.create(self.client, x["member"], user=User.create(self.client, x), guild_id=self.guild_id)
                                                                       if "member" in x else User.create(self.client, x) for x in resp["mentions"]]
        self.mention_roles: typing.List[Snowflake] = [Snowflake(x) for x in resp["mention_roles"]]
        self.mention_channels: typing.List[ChannelMention] = [ChannelMention(x) for x in resp.get("mention_channels", [])]
        self.attachments: typing.List[Attachment] = [Attachment(self.client, x) for x in resp["attachments"] or []]
        self.embeds: typing.List[Embed] = [Embed.create(x) for x in resp["embeds"] or []]
        self.reactions: typing.Optional[typing.List[Reaction]] = [Reaction(self.client, x) for x in resp.get("reactions", [])]
        self.nonce: typing.Optional[typing.Union[int, str]] = resp.get("nonce")
        self.pinned: bool = resp["pinned"]
        self.webhook_id: typing.Optional[Snowflake] = Snowflake.optional(resp.get("webhook_id"))
        self.__webhook_token = webhook_token
        self.__interaction_token = interaction_token
        self.__original_response = original_response
        self.type: MessageTypes = MessageTypes(resp["type"])
        self.activity: typing.Optional[MessageActivity] = MessageActivity.optional(resp.get("activity"))
        self.application: typing.Optional[Application] = resp.get("application")
        self.application_id: typing.Optional[Snowflake] = Snowflake.optional(resp.get("application_id"))
        self.message_reference: typing.Optional[MessageReference] = MessageReference(resp.get("message_reference", {}))
        self.__flags = resp.get("flags")
        self.flags: MessageFlags = MessageFlags.from_value(self.__flags) if self.__flags else self.__flags
        self.__referenced_message = resp.get("referenced_message")
        self.referenced_message: typing.Optional[Message] = Message.create(self.client, self.__referenced_message, guild_id=self.guild_id) if self.__referenced_message else self.__referenced_message
        self.__interaction = resp.get("interaction")
        self.interaction: typing.Optional[MessageInteraction] = MessageInteraction(self.client, self.__interaction) if self.__interaction else self.__interaction
        self.__thread = resp.get("thread")
        self.thread: typing.Optional[Channel] = Channel.create(self.client, self.__thread, guild_id=self.guild_id, ensure_cache_type="channel") if self.__thread else self.__thread
        self.components: typing.Optional[typing.List[Component]] = [Component.auto_detect(x) for x in resp.get("components", [])]
        self.sticker_items: typing.Optional[typing.List[StickerItem]] = [StickerItem(x) for x in resp.get("sticker_items", [])]
        self.stickers: typing.Optional[typing.List[Sticker]] = [Sticker.create(client, x) for x in resp.get("stickers", [])]

        # self.stickers: typing.Optional[typing.List[MessageSticker]] = [MessageSticker(x) for x in resp.get("stickers", [])]

    def __str__(self) -> str:
        return self.content

    def reply(self, content=None, **kwargs) -> "Message.RESPONSE":
        kwargs["message_reference"] = self
        mention = kwargs.pop("mention") if "mention" in kwargs.keys() else True
        allowed_mentions = kwargs.get("allowed_mentions", self.client.default_allowed_mentions or AllowedMentions(replied_user=mention)).copy()
        allowed_mentions.replied_user = mention
        kwargs["allowed_mentions"] = allowed_mentions.to_dict(reply=True)
        return self.client.create_message(self.channel_id, content, **kwargs)

    def edit(self, **kwargs) -> "Message.RESPONSE":
        if self.__webhook_token:
            kwargs["webhook_token"] = self.__webhook_token
            return self.client.edit_webhook_message(self.webhook_id, self, **kwargs)
        elif self.__interaction_token:
            kwargs["interaction_token"] = self.__interaction_token
            if not self.__original_response:
                kwargs["message"] = self
            return self.client.edit_interaction_response(**kwargs)
        return self.client.edit_message(self.channel_id, self.id, **kwargs)

    def delete(self, *, reason: str = None):
        if self.__webhook_token:
            return self.client.delete_webhook_message(self.webhook_id, self, webhook_token=self.__webhook_token)
        elif self.__interaction_token:
            return self.client.delete_interaction_response(interaction_token=self.__interaction_token, message="@original" if self.__original_response else self)
        return self.client.delete_message(self.channel_id, self.id, reason=reason)

    def crosspost(self) -> "Message.RESPONSE":
        return self.client.crosspost_message(self.channel_id, self.id)

    def create_reaction(self, emoji: typing.Union[Emoji, str]):
        return self.client.create_reaction(self.channel_id, self.id, emoji)

    def delete_reaction(self, emoji: typing.Union[Emoji, str], user: User.TYPING = "@me"):
        return self.client.delete_reaction(self.channel_id, self.id, emoji, user)

    def pin(self, *, reason: str = None):
        return self.client.pin_message(self.channel_id, self.id, reason=reason)

    def unpin(self, *, reason: str = None):
        return self.client.unpin_message(self.channel_id, self.id, reason=reason)

    def start_thread(self, *, name: str, auto_archive_duration: int, reason: str = None) -> Channel.RESPONSE:
        return self.client.start_thread(self.channel_id, self, name=name, auto_archive_duration=auto_archive_duration, reason=reason)

    @property
    def guild(self) -> typing.Optional["Guild"]:
        if self.guild_id and self.client.has_cache:
            return self.client.get(self.guild_id, "guild")

    @property
    def channel(self) -> typing.Union[Channel, SendOnlyChannel]:
        send_only = SendOnlyChannel(self.client, self.channel_id)
        if self.channel_id and self.client.has_cache:
            if self.guild_id:
                return self.guild.get(self.channel_id, "channel") or self.client.get(self.channel_id, "channel") or send_only
            else:
                return self.client.get(self.channel_id, "channel") or send_only
        elif self.author and self.client.has_cache:
            return self.client.get(self.author.dm_channel_id, "channel") or send_only
        return send_only

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}>"


class MessageTypes(TypeBase):
    DEFAULT = 0
    RECIPIENT_ADD = 1
    RECIPIENT_REMOVE = 2
    CALL = 3
    CHANNEL_NAME_CHANGE = 4
    CHANNEL_ICON_CHANGE = 5
    CHANNEL_PINNED_MESSAGE = 6
    GUILD_MEMBER_JOIN = 7
    USER_PREMIUM_GUILD_SUBSCRIPTION = 8
    USER_PREMIUM_GUILD_SUBSCRIPTION_TIER_1 = 9
    USER_PREMIUM_GUILD_SUBSCRIPTION_TIER_2 = 10
    USER_PREMIUM_GUILD_SUBSCRIPTION_TIER_3 = 11
    CHANNEL_FOLLOW_ADD = 12
    GUILD_DISCOVERY_DISQUALIFIED = 14
    GUILD_DISCOVERY_REQUALIFIED = 15
    GUILD_DISCOVERY_GRACE_PERIOD_INITIAL_WARNING = 16
    GUILD_DISCOVERY_GRACE_PERIOD_FINAL_WARNING = 17
    THREAD_CREATED = 18
    REPLY = 19
    APPLICATION_COMMAND = 20
    THREAD_STARTER_MESSAGE = 21
    GUILD_INVITE_REMINDER = 22
    CONTEXT_MENU_COMMAND = 23


class MessageActivity:
    def __init__(self, resp: dict):
        self.type: MessageActivityTypes = MessageActivityTypes(resp["type"])
        self.party_id: typing.Optional[str] = resp.get("party_id")  # This is actually set as string in discord docs.

    @classmethod
    def optional(cls, resp):
        if resp:
            return cls(resp)


class MessageActivityTypes(TypeBase):
    JOIN = 1
    SPECTATE = 2
    LISTEN = 3
    JOIN_REQUEST = 4


class MessageFlags(FlagBase):
    CROSSPOSTED = 1 << 0
    IS_CROSSPOST = 1 << 1
    SUPPRESS_EMBEDS = 1 << 2
    SOURCE_MESSAGE_DELETED = 1 << 3
    URGENT = 1 << 4
    HAS_THREAD = 1 << 5
    EPHEMERAL = 1 << 6
    LOADING = 1 << 7


class MessageReference:
    def __init__(self, resp: dict):
        self.message_id: typing.Optional[Snowflake] = Snowflake.optional(resp.get("message_id"))
        self.channel_id: typing.Optional[Snowflake] = Snowflake.optional(resp.get("channel_id"))
        self.guild_id: typing.Optional[Snowflake] = Snowflake.optional(resp.get("guild_id"))
        self.fail_if_not_exists: bool = resp.get("fail_if_not_exists", True)

    def to_dict(self) -> dict:
        resp = {}
        if self.message_id:
            resp["message_id"] = str(self.message_id)
        if self.channel_id:
            resp["channel_id"] = str(self.channel_id)
        if self.guild_id:
            resp["guild_id"] = str(self.guild_id)
        resp["fail_if_not_exists"] = self.fail_if_not_exists
        return resp

    @classmethod
    def from_message(cls, message: Message, fail_if_not_exists: bool = True):
        return cls({"message_id": message.id, "channel_id": message.channel_id, "guild_id": message.guild_id, "fail_if_not_exists": fail_if_not_exists})

    @classmethod
    def from_id(cls, **kwargs):
        return cls(kwargs)


class FollowedChannel:
    RESPONSE = typing.Union["FollowedChannel", typing.Awaitable["FollowedChannel"]]

    def __init__(self, client: "APIClient", resp: dict):
        self.client: "APIClient" = client
        self.channel_id: typing.Optional[Snowflake] = Snowflake(resp["channel_id"])
        self.webhook_id: typing.Optional[Snowflake] = Snowflake(resp["webhook_id"])

    @property
    def channel(self) -> typing.Optional[Channel]:
        if self.client.has_cache:
            return self.client.get(self.channel_id)


class Reaction:
    def __init__(self, client: "APIClient", resp: dict):
        self.count: int = resp["count"]
        self.me: bool = resp["me"]
        self.emoji: Emoji = Emoji(client, resp["emoji"])


class Overwrite(CopyableObject):
    def __init__(self,
                 user: typing.Union[str, int, Snowflake, User] = None,
                 role: typing.Union[str, int, Snowflake, Role] = None,
                 allow: typing.Union[int, PermissionFlags] = 0,
                 deny: typing.Union[int, PermissionFlags] = 0,
                 **kw):
        if user is None and role is None:
            raise TypeError("you must pass user or role.")
        self.id: Snowflake = Snowflake.ensure_snowflake(int(user or role))
        self.type: int = 0 if role else 1
        self.allow: PermissionFlags = PermissionFlags.from_value(int(allow))
        self.deny: PermissionFlags = PermissionFlags.from_value(int(deny))

    def to_dict(self) -> dict:
        return {"id": str(self.id), "type": self.type, "allow": str(int(self.allow)), "deny": str(int(self.deny))}

    def edit(self, **kwargs):
        for k, v in kwargs.items():
            self.allow.__setattr__(k, v)
            self.deny.__setattr__(k, not v)

    @classmethod
    def create(cls, resp: dict):
        resp = resp.copy()
        _id = resp.pop("id")
        _type = resp.pop("type")
        if _type == 1:
            resp["user"] = _id
        elif _type == 0:
            resp["role"] = _id
        return cls(**resp)


class ThreadMetadata:
    def __init__(self, client: "APIClient", resp: dict):
        self.client: "APIClient" = client
        self.archived: bool = resp["archived"]
        # self.archiver_id: typing.Optional[Snowflake] = Snowflake.optional(resp.get("archiver_id"))
        self.auto_archive_duration: int = resp["auto_archive_duration"]
        self.archive_timestamp: datetime.datetime = datetime.datetime.fromisoformat(resp["archive_timestamp"])
        self.locked: bool = resp["locked"]
        self.invitable: typing.Optional[bool] = resp.get("invitable")

    @classmethod
    def optional(cls, client, resp):
        if resp:
            return cls(client, resp)


class ThreadMember:
    RESPONSE = typing.Union["ThreadMember", typing.Awaitable["ThreadMember"]]
    RESPONSE_AS_LIST = typing.Union[typing.List["ThreadMember"], typing.Awaitable[typing.List["ThreadMember"]]]

    def __init__(self, client: "APIClient", resp: dict):
        self.client: "APIClient" = client
        self.id: typing.Optional[Snowflake] = Snowflake.optional(resp.get("id"))
        self.user_id: typing.Optional[Snowflake] = Snowflake.optional(resp.get("user_id"))
        self.join_timestamp: datetime.datetime = datetime.datetime.fromisoformat(resp["join_timestamp"])
        self.flags: int = resp["flags"]

    @property
    def user(self) -> typing.Optional[User]:
        if self.client.has_cache:
            return self.client.get(self.user_id, "user")

    @classmethod
    def optional(cls, client, resp):
        if resp:
            return cls(client, resp)

    @classmethod
    def create(cls, *args):
        """This is just a placeholder to prevent AttributeError."""
        return cls(*args)


class Embed(CopyableObject):
    def __init__(self, *, title: str = None, description: str = None, url: str = None, timestamp: datetime.datetime = None, color: int = None, **kwargs):
        resp = self.__create(title=title, description=description, url=url, timestamp=timestamp, color=color)
        resp.update(kwargs)
        self.title: typing.Optional[str] = resp.get("title")
        self.type: typing.Optional[str] = resp.get("type", "rich")
        self.description: typing.Optional[str] = resp.get("description")
        self.url: typing.Optional[str] = resp.get("url")
        self.__timestamp = resp.get("timestamp")
        self.timestamp: typing.Optional[datetime.datetime] = datetime.datetime.fromisoformat(self.__timestamp) if self.__timestamp else self.__timestamp
        self.color: typing.Optional[int] = resp.get("color")
        self.footer: typing.Optional[EmbedFooter] = EmbedFooter.optional(resp.get("footer"))
        self.image: typing.Optional[EmbedImage] = EmbedImage.optional(resp.get("image"))
        self.thumbnail: typing.Optional[EmbedThumbnail] = EmbedThumbnail.optional(resp.get("thumbnail"))
        self.video: typing.Optional[EmbedVideo] = EmbedVideo.optional(resp.get("video"))
        self.provider: typing.Optional[EmbedProvider] = EmbedProvider.optional(resp.get("provider"))
        self.author: typing.Optional[EmbedAuthor] = EmbedAuthor.optional(resp.get("author"))
        self.fields: typing.Optional[typing.List[EmbedField]] = [EmbedField(x) for x in resp.get("fields", [])]

    @staticmethod
    def __create(*, title: str = None, description: str = None, url: str = None, timestamp: datetime.datetime = None, color: int = None):
        return {"title": title, "description": description, "url": url, "timestamp": str(timestamp) if timestamp else timestamp, "color": color}

    @classmethod
    def create(cls, resp):
        return cls(**resp)

    def set_footer(self, text: str, icon_url: str = None, proxy_icon_url: str = None):
        self.footer = EmbedFooter({"text": text, "icon_url": icon_url, "proxy_icon_url": proxy_icon_url})

    def set_image(self, url: str = None, proxy_url: str = None, height: int = None, width: int = None):
        self.image = EmbedImage({"url": url, "proxy_url": proxy_url, "height": height, "width": width})

    def set_thumbnail(self, url: str = None, proxy_url: str = None, height: int = None, width: int = None):
        self.thumbnail = EmbedThumbnail({"url": url, "proxy_url": proxy_url, "height": height, "width": width})

    def set_video(self, url: str = None, proxy_url: str = None, height: int = None, width: int = None):
        self.video = EmbedVideo({"url": url, "proxy_url": proxy_url, "height": height, "width": width})

    def set_provider(self, name: str = None, url: str = None):
        self.provider = EmbedProvider({"name": name, "url": url})

    def set_author(self, name: str = None, url: str = None, icon_url: str = None, proxy_icon_url: str = None):
        self.author = EmbedAuthor({"name": name, "url": url, "icon_url": icon_url, "proxy_icon_url": proxy_icon_url})

    def add_field(self, name: str, value: str, inline: bool = True):
        self.fields.append(EmbedField({"name": name, "value": value, "inline": inline}))

    @property
    def remove_field(self):
        return self.fields.pop

    def to_dict(self) -> dict:
        ret = {}
        if self.title:
            ret["title"] = self.title
        if self.type:
            ret["type"] = self.type
        if self.description:
            ret["description"] = self.description
        if self.url:
            ret["url"] = self.url
        if self.timestamp:
            ret["timestamp"] = str(self.timestamp)
        if self.color:
            ret["color"] = self.color
        if self.image:
            ret["image"] = self.image.to_dict()
        if self.thumbnail:
            ret["thumbnail"] = self.thumbnail.to_dict()
        if self.video:
            ret["video"] = self.video.to_dict()
        if self.provider:
            ret["provider"] = self.provider.to_dict()
        if self.author:
            ret["author"] = self.author.to_dict()
        if self.fields:
            ret["fields"] = [x.to_dict() for x in self.fields]
        if self.footer:
            ret["footer"] = self.footer.to_dict()
        return ret


class EmbedThumbnail(CopyableObject):
    def __init__(self, resp: dict):
        self.url: typing.Optional[str] = resp.get("url")
        self.proxy_url: typing.Optional[str] = resp.get("proxy_url")
        self.height: typing.Optional[int] = resp.get("height")
        self.width: typing.Optional[int] = resp.get("width")

    def to_dict(self) -> dict:
        ret = {}
        if self.url:
            ret["url"] = self.url
        if self.proxy_url:
            ret["proxy_url"] = self.proxy_url
        if self.height:
            ret["height"] = self.height
        if self.width:
            ret["width"] = self.width
        return ret

    @classmethod
    def optional(cls, resp):
        if resp:
            return cls(resp)


class EmbedVideo(CopyableObject):
    def __init__(self, resp: dict):
        self.url: typing.Optional[str] = resp.get("url")
        self.proxy_url: typing.Optional[str] = resp.get("proxy_url")
        self.height: typing.Optional[int] = resp.get("height")
        self.width: typing.Optional[int] = resp.get("width")

    def to_dict(self) -> dict:
        ret = {}
        if self.url:
            ret["url"] = self.url
        if self.proxy_url:
            ret["proxy_url"] = self.proxy_url
        if self.height:
            ret["height"] = self.height
        if self.width:
            ret["width"] = self.width
        return ret

    @classmethod
    def optional(cls, resp):
        if resp:
            return cls(resp)


class EmbedImage(CopyableObject):
    def __init__(self, resp: dict):
        self.url: typing.Optional[str] = resp.get("url")
        self.proxy_url: typing.Optional[str] = resp.get("proxy_url")
        self.height: typing.Optional[int] = resp.get("height")
        self.width: typing.Optional[int] = resp.get("width")

    def to_dict(self) -> dict:
        ret = {}
        if self.url:
            ret["url"] = self.url
        if self.proxy_url:
            ret["proxy_url"] = self.proxy_url
        if self.height:
            ret["height"] = self.height
        if self.width:
            ret["width"] = self.width
        return ret

    @classmethod
    def optional(cls, resp):
        if resp:
            return cls(resp)


class EmbedProvider(CopyableObject):
    def __init__(self, resp: dict):
        self.name: typing.Optional[str] = resp.get("name")
        self.url: typing.Optional[str] = resp.get("url")

    def to_dict(self) -> dict:
        ret = {}
        if self.name:
            ret["name"] = self.name
        if self.url:
            ret["url"] = self.url
        return ret

    @classmethod
    def optional(cls, resp):
        if resp:
            return cls(resp)


class EmbedAuthor(CopyableObject):
    def __init__(self, resp: dict):
        self.name: typing.Optional[str] = resp.get("name")
        self.url: typing.Optional[str] = resp.get("url")
        self.icon_url: typing.Optional[str] = resp.get("icon_url")
        self.proxy_icon_url: typing.Optional[str] = resp.get("proxy_icon_url")

    def to_dict(self) -> dict:
        ret = {}
        if self.name:
            ret["name"] = self.name
        if self.url:
            ret["url"] = self.url
        if self.icon_url:
            ret["icon_url"] = self.icon_url
        if self.proxy_icon_url:
            ret["proxy_icon_url"] = self.proxy_icon_url
        return ret

    @classmethod
    def optional(cls, resp):
        if resp:
            return cls(resp)


class EmbedFooter(CopyableObject):
    def __init__(self, resp: dict):
        self.text: typing.Optional[str] = resp["text"]
        self.icon_url: typing.Optional[str] = resp.get("icon_url")
        self.proxy_icon_url: typing.Optional[str] = resp.get("proxy_icon_url")

    def to_dict(self) -> dict:
        ret = {"text": self.text}
        if self.icon_url:
            ret["icon_url"] = self.icon_url
        if self.proxy_icon_url:
            ret["proxy_icon_url"] = self.proxy_icon_url
        return ret

    @classmethod
    def optional(cls, resp):
        if resp:
            return cls(resp)


class EmbedField(CopyableObject):
    def __init__(self, resp: dict):
        self.name: typing.Optional[str] = resp["name"]
        self.value: typing.Optional[str] = resp["value"]
        self.inline: typing.Optional[bool] = resp.get("inline", True)

    def to_dict(self) -> dict:
        return {"name": self.name, "value": self.value, "inline": self.inline}

    @classmethod
    def optional(cls, resp):
        if resp:
            return cls(resp)


class Attachment:
    def __init__(self, client: "APIClient", resp: dict):
        self.client: "APIClient" = client
        self.id: Snowflake = Snowflake(resp["id"])
        self.filename: str = resp["filename"]
        self.content_type: typing.Optional[str] = resp.get("content_type")
        self.size: int = resp["size"]
        self.url: str = resp["url"]
        self.proxy_url: str = resp["proxy_url"]
        self.height: typing.Optional[int] = resp.get("height")
        self.width: typing.Optional[int] = resp.get("width")
        self.content: typing.Optional[bytes] = None  # Filled after download is called
        self.ephemeral: typing.Optional[bool] = resp.get("ephemeral")

    def download(self) -> typing.Union[bytes, typing.Awaitable[bytes]]:
        dw = self.client.http.download(self.url)
        if inspect.isawaitable(dw):
            return self.__async_download(dw)
        self.content = dw
        return self.content

    async def __async_download(self, dw):
        self.content = await dw
        return self.content

    def save(self, target: pathlib.Path = ""):
        if self.content is None:
            raise AttributeError("you must download first.")
        with open(str(target)+"/" if target and not str(target).endswith("/") else ""+self.filename, "wb") as f:
            f.write(self.content)

    def to_dict(self) -> dict:
        ret = {"id": str(self.id),
               "filename": self.filename,
               "size": self.size,
               "url": self.url,
               "proxy_url": self.proxy_url}
        if self.content_type:
            ret["content_type"] = self.content_type
        if self.height:
            ret["height"] = self.height
        if self.width:
            ret["width"] = self.width
        return ret


class ChannelMention:
    def __init__(self, resp: dict):
        self.id: Snowflake = Snowflake(resp["id"])
        self.guild_id: Snowflake = Snowflake(resp["guild_id"])
        self.type: ChannelTypes = ChannelTypes(resp["type"])
        self.name: str = resp["name"]


class AllowedMentions(CopyableObject):
    def __init__(self, *,
                 everyone: bool = False,
                 users: typing.List[Snowflake.TYPING] = None,
                 roles: typing.List[Snowflake.TYPING] = None,
                 replied_user: bool = False):
        self.everyone: bool = everyone
        self.users: typing.List[Snowflake.TYPING] = users or []
        self.roles: typing.List[Snowflake.TYPING] = roles or []
        self.replied_user: bool = replied_user

    def to_dict(self, *, reply: bool = False) -> dict:
        ret = {"parsed": []}
        if self.everyone:
            ret["parsed"].append("everyone")
        if self.users:
            ret["parsed"].append("users")
            ret["users"] = [str(x) for x in self.users]
        if self.roles:
            ret["parsed"].append("roles")
            ret["roles"] = [str(x) for x in self.roles]
        if reply:
            ret["replied_user"] = self.replied_user
        return ret


class ListThreadsResponse:
    RESPONSE = typing.Union["ListThreadsResponse", typing.Awaitable["ListThreadsResponse"]]

    def __init__(self, client: "APIClient", resp: dict):
        self.threads: typing.List[Channel] = [Channel.create(client, x) for x in resp["threads"]]
        self.members: typing.List[ThreadMember] = [ThreadMember(client, x) for x in resp["members"]]
        self.has_more: typing.Optional[bool] = resp.get("has_more")
