import inspect
import pathlib
import datetime

from typing import TYPE_CHECKING, Optional, Union, List, Awaitable, overload

from .emoji import Emoji
from .guild import GuildMember, WelcomeScreenChannel
from .permission import PermissionFlags, Role
from .snowflake import Snowflake
from .sticker import Sticker, StickerItem
from .user import User
from ..base.model import CopyableObject, DiscordObjectBase, TypeBase, FlagBase
from ..base.http import EmptyObject
from ..utils import from_emoji

if TYPE_CHECKING:
    from .application import Application
    from .guild import Guild
    from .invite import Invite
    from ..api import APIClient


class Channel(DiscordObjectBase):
    """
    Represents a Discord channel.

    Refer https://discord.com/developers/docs/resources/channel#channel-object-channel-structure for attributes of the channel object.
    """

    TYPING = Union[int, str, Snowflake, "Channel"]
    RESPONSE = Union["Channel", Awaitable["Channel"]]
    RESPONSE_AS_LIST = Union[List["Channel"], Awaitable[List["Channel"]]]
    _cache_type = "channel"

    def __init__(self, client: "APIClient", resp: dict, *, guild_id: Snowflake.TYPING = None):
        super().__init__(client, resp)
        self.type: ChannelTypes = ChannelTypes(resp["type"])
        self.guild_id: Snowflake = Snowflake.optional(resp.get("guild_id")) or Snowflake.ensure_snowflake(guild_id)
        self.position: Optional[int] = resp.get("position")
        self.permission_overwrites: Optional[List[Overwrite]] = [Overwrite.create(x) for x in resp.get("permission_overwrites", [])]
        self.name: Optional[str] = resp.get("name")
        self.topic: Optional[str] = resp.get("topic")
        self.nsfw: Optional[bool] = resp.get("nsfw")
        self.last_message_id: Optional[Snowflake] = Snowflake.optional(resp.get("last_message_id"))
        self.bitrate: Optional[int] = resp.get("bitrate")
        self.user_limit: Optional[int] = resp.get("user_limit")
        self.rate_limit_per_user: Optional[int] = resp.get("rate_limit_per_user")
        self.recipients: Optional[List[User]] = [User.create(client, x) for x in resp.get("recipients", [])]
        self.icon: Optional[str] = resp.get("icon")
        self.owner_id: Optional[Snowflake] = Snowflake.optional(resp.get("owner_id"))
        self.application_id: Optional[Snowflake] = Snowflake.optional(resp.get("application_id"))
        self.parent_id: Optional[Snowflake] = Snowflake.optional(resp.get("parent_id"))
        self.__last_pin_timestamp = resp.get("last_pin_timestamp")
        self.last_pin_timestamp: Optional[datetime.datetime] = datetime.datetime.fromisoformat(self.__last_pin_timestamp) if self.__last_pin_timestamp else self.__last_pin_timestamp
        self.rtc_region: Optional[str] = resp.get("rtc_region")
        self.__video_quality_mode = resp.get("video_quality_mode")
        self.video_quality_mode: Optional[VideoQualityModes] = VideoQualityModes(self.__video_quality_mode) if self.__video_quality_mode else self.__video_quality_mode
        self.message_count: Optional[int] = resp.get("message_count")
        self.member_count: Optional[int] = resp.get("member_count")
        self.thread_metadata: Optional[ThreadMetadata] = ThreadMetadata.optional(self.client, resp.get("thread_metadata"))
        self.member: Optional[ThreadMember] = ThreadMember.optional(self.client, resp.get("member"))
        self.default_auto_archive_duration: Optional[int] = resp.get("default_auto_archive_duration")
        self.__permissions = resp.get("permissions")
        self.permissions: Optional[PermissionFlags] = PermissionFlags.from_value(int(self.__permissions)) if self.__permissions else self.__permissions

        # if self.type.dm and self.

    def __str__(self) -> str:
        return self.name

    @overload
    def modify(self,
               *,
               name: Optional[str] = None,
               channel_type: Optional[Union[int, "ChannelTypes"]] = None,
               position: Optional[int] = EmptyObject,
               topic: Optional[str] = EmptyObject,
               nsfw: Optional[bool] = EmptyObject,
               rate_limit_per_user: Optional[int] = EmptyObject,
               bitrate: Optional[int] = EmptyObject,
               user_limit: Optional[int] = EmptyObject,
               permission_overwrites: Optional[List["Overwrite"]] = EmptyObject,
               parent: Optional[TYPING] = EmptyObject,
               rtc_region: Optional[str] = EmptyObject,
               video_quality_mode: Optional[Union[int, "VideoQualityModes"]] = EmptyObject,
               reason: Optional[str] = None) -> RESPONSE:
        """
        Modifies guild channel.

        .. note::
            All keyword-only arguments except name, channel_type, and reason accept None.

        :param Optional[str] name: Name of the channel to change.
        :param Optional[ChannelTypes] channel_type: Type of the channel to change.
        :param Optional[int] position: Position of the channel to change.
        :param Optional[str] topic: Topic of the channel to change.
        :param Optional[bool] nsfw: Whether this channel is NSFW.
        :param Optional[int] rate_limit_per_user: Slowmode of the channel to change.
        :param Optional[int] bitrate: Bitrate of the channel to change.
        :param Optional[int] user_limit: User limit of the channel to change.
        :param Optional[List[Overwrite]] permission_overwrites: List of permission overwrites to change.
        :param parent: Parent category of the channel to change.
        :param Optional[str] rtc_region: RTC region of the channel to change. Pass None to set to automatic.
        :param Optional[VideoQualityModes] video_quality_mode: Video quality mode of the camera to change.
        :param Optional[str] reason: Reason of the action.
        :return: :class:`~.Channel`
        """
        ...

    @overload
    def modify(self, *, name: Optional[str] = None, icon: Optional[bytes] = None, reason: Optional[str] = None) -> RESPONSE:
        """
        Modifies group DM channel.

        :param Optional[str] name: Name to change.
        :param Optional[bin] icon: Icon as bytes to change.
        :param Optional[str] reason: Reason of the action.
        :return: :class:`~.Channel`
        """
        ...

    @overload
    def modify(self,
               *,
               name: Optional[str] = None,
               archived: Optional[bool] = None,
               auto_archive_duration: Optional[int] = None,
               locked: Optional[bool] = None,
               rate_limit_per_user: Optional[int] = EmptyObject,
               reason: Optional[str] = None) -> RESPONSE:
        """
        Modifies thread channel.

        :param Optional[str] name: Name to change.
        :param archived: Whether this thread is archived.
        :param Optional[int] auto_archive_duration: Auto archive duration to set.
        :param Optional[bool] locked: Whether this thread is locked.
        :param Optional[int] rate_limit_per_user: Slowmode time to change. Set to None to remove.
        :param Optional[str] reason: Reason of the action.
        :return: :class:`~.Channel`
        """
        ...

    def modify(self, **kwargs) -> RESPONSE:
        """
        Modifies channel.
        
        .. note::
            ``**kwargs`` varies depending on the channel type.
        :return: :class:`~.Channel`
        """
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
        """Alias of :meth:`.modify`."""
        return self.modify

    def delete(self, *, reason: Optional[str] = None) -> RESPONSE:
        """
        Deletes channel.

        :param Optional[str] reason: Reason of the action.
        :return: :class:`~.Channel`
        """
        return self.client.delete_channel(self, reason=reason)

    def create_message(self, *args, **kwargs) -> "Message.RESPONSE":
        """
        Creates message.

        .. note::
            - FileIO object passed to ``file`` or ``files`` parameter will be automatically closed when requesting,
              therefore it is recommended to pass file path.

        .. warning::
            - You must pass at least one of ``content`` or ``embed`` or ``file`` or ``files`` parameter.
            - You can't use ``file`` and ``files`` at the same time.

        :param Optional[str] content: Content of the message.
        :param embed: Embed of the message.
        :type embed: Optional[Union[Embed, dict]]
        :param embeds: List of embeds of the message.
        :type embeds: Optional[List[Union[Embed, dict]]]
        :param file: File of the message.
        :type file: Optional[Union[io.FileIO, pathlib.Path, str]]
        :param files: Files of the message.
        :type files: Optional[List[Union[io.FileIO, pathlib.Path, str]]]
        :param Optional[bool] tts: Whether to speak message.
        :param allowed_mentions: :class:`~.AllowedMentions` to use for this request.
        :type allowed_mentions: Optional[Union[AllowedMentions, dict]]
        :param message_reference: Message to reply.
        :type message_reference: Optional[Union[Message, MessageReference, dict]]
        :param component: Component of the message.
        :type component: Optional[Union[dict, Component]]
        :param components: List of  components of the message.
        :type components: Optional[List[Union[dict, Component]]]
        :param Optional[Sticker] sticker: Sticker of the message.
        :param Optional[List[Sticker]] stickers: Stickers of the message. Up to 3.
        :return: :class:`~.Message`
        """
        if not self.is_messageable():
            raise TypeError("You can't send message in this type of channel.")
        return self.client.create_message(self, *args, **kwargs)

    @property
    def send(self):
        """Alias of :meth:`.create_message`."""
        return self.create_message

    def bulk_delete_messages(self, *messages: "Message.TYPING", reason: Optional[str] = None):
        """
        Bulk deletes messages.

        :param messages: Messages to delete.
        :param Optional[str] reason: Reason of the action.
        """
        return self.client.bulk_delete_messages(self, *messages, reason=reason)

    def edit_permissions(self, overwrite, *, reason: Optional[str] = None):
        """
        Edits permissions.

        :param Overwrite overwrite: Permission overwrite to edit.
        :param Optional[str] reason: Reason of the action.
        """
        return self.client.edit_channel_permissions(self, overwrite, reason=reason)

    def request_invites(self) -> "Invite.RESPONSE_AS_LIST":
        """
        Requests channel invites.

        :return: List[:class:`~.Invite`]
        """
        return self.client.request_channel_invites(self)

    def create_invite(self, **kwargs) -> "Invite.RESPONSE":
        """
        Creates channel invite.

        :param Optional[int] max_age: Maximum age of the invite.
        :param Optional[int] max_uses: Maximum use count of the invite.
        :param Optional[bool] temporary: Whether this invite is temporary, meaning user will be kicked if role is not added.
        :param Optional[bool] unique: Whether this invite is unique, meaning new code will be generated even if there is invite with same options.
        :param target_type: Target type of the voice channel invite.
        :type target_type: Optional[Union[int, InviteTargetTypes]]
        :param target_user: Target user of the invite.
        :param target_application: Target application of the invite.
        :param Optional[str] reason: Reason of the action.
        :return: :class:`~.Invite`
        """
        return self.client.create_channel_invite(self, **kwargs)

    def delete_permissions(self, overwrite, *, reason: Optional[str] = None):
        """
        Deletes permissions.

        :param overwrite: Target overwrite to delete. Accepts ID of the user or role.
        :param Optional[str] reason: Reason of the action.
        """
        return self.client.delete_channel_permission(self, overwrite, reason=reason)

    def follow(self, target_channel: "Channel.TYPING") -> "FollowedChannel.RESPONSE":
        """
        Follows this channel to target channel.
        :param target_channel: Channel to receive published messages.
        :return: :class:`~.FollowedChannel`
        """
        return self.client.follow_news_channel(self, target_channel)

    def trigger_typing_indicator(self):
        """
        Triggers ``<client> is typing...`` on channel.
        """
        return self.client.trigger_typing_indicator(self)

    def request_pinned_messages(self) -> "Message.RESPONSE_AS_LIST":
        """
        Requests pinned messages.

        :return: List[:class:`~.Message`]
        """
        return self.client.request_pinned_messages(self)

    def add_recipient(self, user: User.TYPING, access_token: str, nick: str):
        """
        Adds recipient to the group DM.

        :param user: Recipient to add.

        :param str access_token: OAuth2 access token to use.
        :param str nick: Nickname to assign.
        """
        if not self.type.group_dm:
            raise AttributeError("This type of channel is not allowed to add recipient.")
        return self.client.group_dm_add_recipient(self, user, access_token, nick)

    def remove_recipient(self, user: User.TYPING):
        """
        Removes recipient from the group DM.

        :param user: Recipient to remove.
        """
        if not self.type.group_dm:
            raise AttributeError("This type of channel is not allowed to remove recipient.")
        return self.client.group_dm_remove_recipient(self, user)

    def start_thread(self, message: "Message.TYPING" = None, *, name: str, auto_archive_duration: int, reason: Optional[str] = None) -> "Channel.RESPONSE":
        """
        Starts new thread.

        .. note::
            If ``message`` param is passed, type of thread will be always public regardless of what you've set to.

        :param message: Message to create thread from.
        :param str name: Name of the thread.
        :param int auto_archive_duration: When to archive thread in minutes.
        :param Optional[str] reason: Reason of the action.
        :return: :class:`~.Channel`
        """
        return self.client.start_thread(self, message, name=name, auto_archive_duration=auto_archive_duration, reason=reason)

    def join_thread(self):
        """
        Joins to thread.
        """
        if not self.is_thread_channel():
            raise AttributeError("This type of channel is not allowed to join thread.")
        return self.client.join_thread(self)

    def add_thread_member(self, user: User.TYPING):
        """
        Adds member to thread.

        :param user: User to add.
        """
        if not self.is_thread_channel():
            raise AttributeError("This type of channel is not allowed to add thread member.")
        return self.client.add_thread_member(self, user)

    def leave_thread(self):
        """
        Leaves thread.
        """
        if not self.is_thread_channel():
            raise AttributeError("This type of channel is not allowed to leave thread.")
        return self.client.leave_thread(self)

    def remove_thread_member(self, user: User.TYPING):
        """
        Removes member from thread.

        :param user: User to remove.
        """
        if not self.is_thread_channel():
            raise AttributeError("This type of channel is not allowed to remove thread member.")
        return self.client.remove_thread_member(self, user)

    def list_thread_members(self) -> "ThreadMember.RESPONSE_AS_LIST":
        """
        Returns list of members in thread.

        :return: List[:class:`~.ThreadMember`]
        """
        if not self.is_thread_channel():
            raise AttributeError("This type of channel is not allowed to list thread members.")
        return self.client.list_thread_members(self)

    def list_active_threads(self) -> "ListThreadsResponse.RESPONSE":
        """
        Returns list of active threads in channel.

        :return: :class:`~.ListThreadsResponse`
        """
        return self.client.list_active_threads(self)

    def list_public_archived_threads(self, *, before: Optional[Union[str, datetime.datetime]] = None, limit: Optional[int] = None) -> "ListThreadsResponse.RESPONSE":
        """
        Returns list of public archived threads in channel.

        :param before: Timestamp to show threads before.
        :type before: Optional[Union[str, datetime.datetime]]
        :param Optional[int] limit: Limit of the number of the threads.
        :return: :class:`~.ListThreadsResponse`
        """
        return self.client.list_public_archived_threads(self, before=before, limit=limit)

    def list_private_archived_threads(self, *, before: Optional[Union[str, datetime.datetime]] = None, limit: Optional[int] = None) -> "ListThreadsResponse.RESPONSE":
        """
        Returns list of private archived threads in channel.

        :param before: Timestamp to show threads before.
        :type before: Optional[Union[str, datetime.datetime]]
        :param Optional[int] limit: Limit of the number of the threads.
        :return: :class:`~.ListThreadsResponse`
        """
        return self.client.list_private_archived_threads(self, before=before, limit=limit)

    def list_joined_private_archived_threads(self, *, before: Optional[Union[str, datetime.datetime]] = None, limit: Optional[int] = None) -> "ListThreadsResponse.RESPONSE":
        """
        Returns list of private archived threads that bot joined in channel.

        :param before: Timestamp to show threads before.
        :type before: Optional[Union[str, datetime.datetime]]
        :param Optional[int] limit: Limit of the number of the threads.
        :return: :class:`~.ListThreadsResponse`
        """
        return self.client.list_joined_private_archived_threads(self, before=before, limit=limit)

    def archive(self, locked: bool = False):
        """
        Archives thread.

        :param bool locked: whether to lock thread or not.
        """
        if not self.is_thread_channel():
            raise AttributeError("This type of channel is not allowed to archive.")
        return self.modify(archived=True, locked=locked)

    def to_position_param(self, position: Optional[int] = None, lock_permissions: Optional[bool] = None, parent: Optional["Channel.TYPING"] = None) -> dict:
        """
        Exports channel object to dict as position parameter format.

        :param Optional[int] position: Position of the channel.
        :param Optional[bool] lock_permissions: Whether to lock permissions.
        :param parent: Parent category of the channel.
        :return: dict
        """
        if isinstance(parent, Channel) and not parent.type.guild_category:
            raise TypeError("parent must be category channel.")
        param = {
            "id": str(self.id),
            "position": position,
            "lock_permissions": lock_permissions,
            "parent_id": str(int(parent))
        }
        return param

    def to_welcome_screen_channel(self, description: str, emoji: Optional[Emoji.TYPING] = None) -> WelcomeScreenChannel:
        """
        Exports channel object to welcome screen object.

        :param str description: Description of the channel.
        :param emoji: Emoji to use.
        :return: :class:`~.WelcomeScreenChannel`
        """
        emoji = from_emoji(emoji)
        emoji_id = emoji.split(":")[-1] if ":" in emoji else None
        emoji_name = emoji.split(":")[-2] if ":" in emoji else emoji
        return WelcomeScreenChannel({"channel_id": str(self.id), "description": description, "emoji_id": emoji_id, "emoji_name": emoji_name})

    @property
    def mention(self) -> str:
        """
        The string that mentions channel.

        """
        return f"<#{self.id}>"

    @property
    def guild(self) -> Optional["Guild"]:
        """
        Guild that channel belongs to if applicable.

        """
        if self.guild_id and self.client.has_cache:
            return self.client.cache.get(self.guild_id, "guild")  # noqa

    def is_messageable(self) -> bool:
        """
        Checks if channel is able to send messages.

        :return: bool
        """
        if self.is_thread_channel():
            return self.thread_metadata.archived
        return self.type.guild_text or self.type.guild_news or self.type.dm or self.type.group_dm

    def is_thread_channel(self) -> bool:
        """
        Checks if channel is a thread.

        :return: bool
        """
        return self.type.guild_news_thread or self.type.guild_public_thread or self.type.guild_private_thread

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} id={self.id} name={self.name}>'


class ChannelTypes(TypeBase):
    """
    Types of the channel.
    """
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
    """
    Types of the video quality modes.
    """
    AUTO = 1
    FULL = 2


class SendOnlyChannel:
    """
    Internal class representing temporary messageable channel.
    """
    def __init__(self, client: "APIClient", channel_id: Snowflake.TYPING):
        self.client: "APIClient" = client
        self.id: Snowflake = Snowflake.ensure_snowflake(channel_id)

    def __int__(self) -> int:
        return int(self.id)

    def send(self, *args, **kwargs) -> "Message.RESPONSE":
        return self.client.create_message(self.id, *args, **kwargs)

    def __getattr__(self, item):
        return None


class Message(DiscordObjectBase):
    """
    Represents a Discord message.

    Refer https://discord.com/developers/docs/resources/channel#message-object for attributes of the channel object.
    """

    TYPING = Union[int, str, Snowflake, "Message"]
    RESPONSE = Union["Message", Awaitable["Message"]]
    RESPONSE_AS_LIST = Union[List["Message"], Awaitable[List["Message"]]]
    _cache_type = "message"

    def __init__(self,
                 client: "APIClient",
                 resp: dict,
                 *,
                 guild_id: Snowflake.TYPING = None,
                 webhook_token: Optional[str] = None,
                 interaction_token: Optional[str] = None,
                 original_response: Optional[bool] = False):
        from .interactions import MessageInteraction, Component  # Prevent circular import.
        super().__init__(client, resp)
        self.channel_id: Snowflake = Snowflake(resp["channel_id"])
        self.guild_id: Optional[Snowflake] = Snowflake.optional(resp.get("guild_id") or guild_id)
        self.author: User = User.create(client, resp["author"])
        self.__member = resp.get("member")
        self.member: GuildMember = GuildMember.create(self.client, self.__member, user=self.author, guild_id=self.guild_id) if self.__member else self.__member
        self.content: str = resp["content"]
        self.timestamp: datetime.datetime = datetime.datetime.fromisoformat(resp["timestamp"])
        self.__edited_timestamp = resp["edited_timestamp"]
        self.edited_timestamp: Optional[datetime.datetime] = datetime.datetime.fromisoformat(self.__edited_timestamp) if self.__edited_timestamp else self.__edited_timestamp
        self.tts: bool = resp["tts"]
        self.mention_everyone: bool = resp["mention_everyone"]
        self.mentions: List[Union[User, GuildMember]] = [GuildMember.create(self.client, x["member"], user=User.create(self.client, x), guild_id=self.guild_id)
                                                         if "member" in x else User.create(self.client, x) for x in resp["mentions"]]
        self.mention_roles: List[Snowflake] = [Snowflake(x) for x in resp["mention_roles"]]
        self.mention_channels: List[ChannelMention] = [ChannelMention(x) for x in resp.get("mention_channels", [])]
        self.attachments: List[Attachment] = [Attachment(self.client, x) for x in resp["attachments"] or []]
        self.embeds: List[Embed] = [Embed.create(x) for x in resp["embeds"] or []]
        self.reactions: Optional[List[Reaction]] = [Reaction(self.client, x) for x in resp.get("reactions", [])]
        self.nonce: Optional[Union[int, str]] = resp.get("nonce")
        self.pinned: bool = resp["pinned"]
        self.webhook_id: Optional[Snowflake] = Snowflake.optional(resp.get("webhook_id"))
        self.__webhook_token = webhook_token
        self.__interaction_token = interaction_token
        self.__original_response = original_response
        self.type: MessageTypes = MessageTypes(resp["type"])
        self.activity: Optional[MessageActivity] = MessageActivity.optional(resp.get("activity"))
        self.application: Optional[Application] = resp.get("application")
        self.application_id: Optional[Snowflake] = Snowflake.optional(resp.get("application_id"))
        self.message_reference: Optional[MessageReference] = MessageReference(resp.get("message_reference", {}))
        self.__flags = resp.get("flags")
        self.flags: MessageFlags = MessageFlags.from_value(self.__flags) if self.__flags else self.__flags
        self.__referenced_message = resp.get("referenced_message")
        self.referenced_message: Optional[Message] = Message.create(self.client, self.__referenced_message, guild_id=self.guild_id) if self.__referenced_message else self.__referenced_message
        self.__interaction = resp.get("interaction")
        self.interaction: Optional[MessageInteraction] = MessageInteraction(self.client, self.__interaction) if self.__interaction else self.__interaction
        self.__thread = resp.get("thread")
        self.thread: Optional[Channel] = Channel.create(self.client, self.__thread, guild_id=self.guild_id, ensure_cache_type="channel") if self.__thread else self.__thread
        self.components: Optional[List[Component]] = [Component.auto_detect(x) for x in resp.get("components", [])]
        self.sticker_items: Optional[List[StickerItem]] = [StickerItem(x) for x in resp.get("sticker_items", [])]
        self.stickers: Optional[List[Sticker]] = [Sticker.create(client, x) for x in resp.get("stickers", [])]

        # self.stickers: Optional[List[MessageSticker]] = [MessageSticker(x) for x in resp.get("stickers", [])]

    def __str__(self) -> str:
        return self.content

    def reply(self, content: Optional[str] = None, **kwargs) -> "Message.RESPONSE":
        """
        Replies to the message.

        :param Optional[str] content: Content of the message.
        :param embed: Embed of the message.
        :type embed: Optional[Union[Embed, dict]]
        :param embeds: List of embeds of the message.
        :type embeds: Optional[List[Union[Embed, dict]]]
        :param file: File of the message.
        :type file: Optional[Union[io.FileIO, pathlib.Path, str]]
        :param files: Files of the message.
        :type files: Optional[List[Union[io.FileIO, pathlib.Path, str]]]
        :param Optional[bool] tts: Whether to speak message.
        :param allowed_mentions: :class:`~.AllowedMentions` to use for this request.
        :type allowed_mentions: Optional[Union[AllowedMentions, dict]]
        :param component: Component of the message.
        :type component: Optional[Union[dict, Component]]
        :param components: List of  components of the message.
        :type components: Optional[List[Union[dict, Component]]]
        :param Optional[Sticker] sticker: Sticker of the message.
        :param Optional[List[Sticker]] stickers: Stickers of the message. Up to 3.
        :return: :class:`~.Message`
        """
        kwargs["message_reference"] = self
        mention = kwargs.pop("mention") if "mention" in kwargs.keys() else True
        allowed_mentions = kwargs.get("allowed_mentions", self.client.default_allowed_mentions or AllowedMentions(replied_user=mention)).copy()
        allowed_mentions.replied_user = mention
        kwargs["allowed_mentions"] = allowed_mentions.to_dict(reply=True)
        return self.client.create_message(self.channel_id, content, **kwargs)

    def edit(self, **kwargs) -> "Message.RESPONSE":
        """
        Edits message.
        
        :param Optional[str] content: Content to edit.
        :param embed: Embed to edit.
        :type embed: Optional[Union[Embed, dict]]
        :param embeds: Embeds to edit.
        :type embeds: Optional[List[Union[Embed, dict]]]
        :param Optional[FILE_TYPE] file: File to add.
        :param Optional[List[FILE_TYPE]] files: Files to add.
        :param allowed_mentions: Allowed mentions of the message.
        :type allowed_mentions: Optional[Union[AllowedMentions, dict]]
        :param attachments: Attachments to keep.
        :type attachments: Optional[List[Union[Attachment, dict]]]
        :param component: Component of the message to edit.
        :type component: Optional[Union[dict, Component]]
        :param components: Components of the message to edit.
        :type components: Optional[List[Union[dict, Component]]]
        :return: :class:`~.Message`
        """
        if self.__webhook_token:
            kwargs["webhook_token"] = self.__webhook_token
            return self.client.edit_webhook_message(self.webhook_id, self, **kwargs)
        elif self.__interaction_token:
            kwargs["interaction_token"] = self.__interaction_token
            if not self.__original_response:
                kwargs["message"] = self
            return self.client.edit_interaction_response(**kwargs)
        return self.client.edit_message(self.channel_id, self.id, **kwargs)

    def delete(self, *, reason: Optional[str] = None):
        """
        Deletes message.

        :param Optional[str] reason: Reason of the action.
        """
        if self.__webhook_token:
            return self.client.delete_webhook_message(self.webhook_id, self, webhook_token=self.__webhook_token)
        elif self.__interaction_token:
            return self.client.delete_interaction_response(interaction_token=self.__interaction_token, message="@original" if self.__original_response else self)
        return self.client.delete_message(self.channel_id, self.id, reason=reason)

    def crosspost(self) -> "Message.RESPONSE":
        """
        Crossposts message.

        :return: :class:`~.Message`
        """
        return self.client.crosspost_message(self.channel_id, self.id)

    def create_reaction(self, emoji: Union[Emoji, str]):
        """
        Creates reaction.

        :param emoji: Emoji for creating reaction.
        :type emoji: Union[str, Emoji]
        """
        return self.client.create_reaction(self.channel_id, self.id, emoji)

    def delete_reaction(self, emoji: Union[Emoji, str], user: User.TYPING = "@me"):
        """
        Deletes reaction.

        :param emoji: Emoji of the reaction to delete.
        :type emoji: Union[str, Emoji]
        :param user: User to delete reaction of. Default "@me" which is the bot itself.
        """
        return self.client.delete_reaction(self.channel_id, self.id, emoji, user)

    def pin(self, *, reason: Optional[str] = None):
        """
        Pins message.

        :param Optional[str] reason: Reason of the action.
        """
        return self.client.pin_message(self.channel_id, self.id, reason=reason)

    def unpin(self, *, reason: Optional[str] = None):
        """
        Unpins message.

        :param Optional[str] reason: Reason of the action.
        """
        return self.client.unpin_message(self.channel_id, self.id, reason=reason)

    def start_thread(self, *, name: str, auto_archive_duration: int, reason: Optional[str] = None) -> Channel.RESPONSE:
        """
        Starts new thread.
        
        :param str name: Name of the thread.
        :param int auto_archive_duration: When to archive thread in minutes.
        :param Optional[str] reason: Reason of the action.
        :return: :class:`~.Channel`
        """
        return self.client.start_thread(self.channel_id, self, name=name, auto_archive_duration=auto_archive_duration, reason=reason)

    @property
    def guild(self) -> Optional["Guild"]:
        """Guild this message belongs to."""
        if self.guild_id and self.client.has_cache:
            return self.client.get(self.guild_id, "guild")

    @property
    def channel(self) -> Union[Channel, SendOnlyChannel]:
        """Channel this message belongs to."""
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
    """
    Types of the message.
    """
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
    """
    Represents Message Activity.

    :ivar MessageActivityTypes ~.type: Type of the message activity.
    :ivar Optional[str] ~.party_id: ID of the party.
    """
    def __init__(self, resp: dict):
        self.type: MessageActivityTypes = MessageActivityTypes(resp["type"])
        self.party_id: Optional[str] = resp.get("party_id")  # This is actually set as string in discord docs.

    @classmethod
    def optional(cls, resp):
        if resp:
            return cls(resp)


class MessageActivityTypes(TypeBase):
    """
    Types of the message activity.
    """
    JOIN = 1
    SPECTATE = 2
    LISTEN = 3
    JOIN_REQUEST = 5


class MessageFlags(FlagBase):
    """
    Flags of the message.
    """
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
        self.message_id: Optional[Snowflake] = Snowflake.optional(resp.get("message_id"))
        self.channel_id: Optional[Snowflake] = Snowflake.optional(resp.get("channel_id"))
        self.guild_id: Optional[Snowflake] = Snowflake.optional(resp.get("guild_id"))
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
    RESPONSE = Union["FollowedChannel", Awaitable["FollowedChannel"]]

    def __init__(self, client: "APIClient", resp: dict):
        self.client: "APIClient" = client
        self.channel_id: Optional[Snowflake] = Snowflake(resp["channel_id"])
        self.webhook_id: Optional[Snowflake] = Snowflake(resp["webhook_id"])

    @property
    def channel(self) -> Optional[Channel]:
        if self.client.has_cache:
            return self.client.get(self.channel_id)


class Reaction:
    def __init__(self, client: "APIClient", resp: dict):
        self.count: int = resp["count"]
        self.me: bool = resp["me"]
        self.emoji: Emoji = Emoji(client, resp["emoji"])


class Overwrite(CopyableObject):
    TYPING = Union[int, str, Snowflake, "Overwrite"]

    def __init__(self,
                 user: Union[str, int, Snowflake, User] = None,
                 role: Union[str, int, Snowflake, Role] = None,
                 allow: Union[int, PermissionFlags] = 0,
                 deny: Union[int, PermissionFlags] = 0,
                 **kw):
        if user is None and role is None:
            raise TypeError("you must pass user or role.")
        self.id: Snowflake = Snowflake.ensure_snowflake(int(user or role))
        self.type: int = 0 if role else 1
        self.allow: PermissionFlags = PermissionFlags.from_value(int(allow))
        self.deny: PermissionFlags = PermissionFlags.from_value(int(deny))

    def __int__(self) -> int:
        return int(self.id)

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
        # self.archiver_id: Optional[Snowflake] = Snowflake.optional(resp.get("archiver_id"))
        self.auto_archive_duration: int = resp["auto_archive_duration"]
        self.archive_timestamp: datetime.datetime = datetime.datetime.fromisoformat(resp["archive_timestamp"])
        self.locked: bool = resp["locked"]
        self.invitable: Optional[bool] = resp.get("invitable")

    @classmethod
    def optional(cls, client, resp):
        if resp:
            return cls(client, resp)


class ThreadMember:
    RESPONSE = Union["ThreadMember", Awaitable["ThreadMember"]]
    RESPONSE_AS_LIST = Union[List["ThreadMember"], Awaitable[List["ThreadMember"]]]

    def __init__(self, client: "APIClient", resp: dict):
        self.client: "APIClient" = client
        self.id: Optional[Snowflake] = Snowflake.optional(resp.get("id"))
        self.user_id: Optional[Snowflake] = Snowflake.optional(resp.get("user_id"))
        self.join_timestamp: datetime.datetime = datetime.datetime.fromisoformat(resp["join_timestamp"])
        self.flags: int = resp["flags"]

    @property
    def user(self) -> Optional[User]:
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
        self.title: Optional[str] = resp.get("title")
        self.type: Optional[str] = resp.get("type", "rich")
        self.description: Optional[str] = resp.get("description")
        self.url: Optional[str] = resp.get("url")
        self.__timestamp = resp.get("timestamp")
        self.timestamp: Optional[datetime.datetime] = datetime.datetime.fromisoformat(self.__timestamp) if self.__timestamp else self.__timestamp
        self.color: Optional[int] = resp.get("color")
        self.footer: Optional[EmbedFooter] = EmbedFooter.optional(resp.get("footer"))
        self.image: Optional[EmbedImage] = EmbedImage.optional(resp.get("image"))
        self.thumbnail: Optional[EmbedThumbnail] = EmbedThumbnail.optional(resp.get("thumbnail"))
        self.video: Optional[EmbedVideo] = EmbedVideo.optional(resp.get("video"))
        self.provider: Optional[EmbedProvider] = EmbedProvider.optional(resp.get("provider"))
        self.author: Optional[EmbedAuthor] = EmbedAuthor.optional(resp.get("author"))
        self.fields: Optional[List[EmbedField]] = [EmbedField(x) for x in resp.get("fields", [])]

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
        self.url: Optional[str] = resp.get("url")
        self.proxy_url: Optional[str] = resp.get("proxy_url")
        self.height: Optional[int] = resp.get("height")
        self.width: Optional[int] = resp.get("width")

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
        self.url: Optional[str] = resp.get("url")
        self.proxy_url: Optional[str] = resp.get("proxy_url")
        self.height: Optional[int] = resp.get("height")
        self.width: Optional[int] = resp.get("width")

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
        self.url: Optional[str] = resp.get("url")
        self.proxy_url: Optional[str] = resp.get("proxy_url")
        self.height: Optional[int] = resp.get("height")
        self.width: Optional[int] = resp.get("width")

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
        self.name: Optional[str] = resp.get("name")
        self.url: Optional[str] = resp.get("url")

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
        self.name: Optional[str] = resp.get("name")
        self.url: Optional[str] = resp.get("url")
        self.icon_url: Optional[str] = resp.get("icon_url")
        self.proxy_icon_url: Optional[str] = resp.get("proxy_icon_url")

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
        self.text: Optional[str] = resp["text"]
        self.icon_url: Optional[str] = resp.get("icon_url")
        self.proxy_icon_url: Optional[str] = resp.get("proxy_icon_url")

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
        self.name: Optional[str] = resp["name"]
        self.value: Optional[str] = resp["value"]
        self.inline: Optional[bool] = resp.get("inline", True)

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
        self.content_type: Optional[str] = resp.get("content_type")
        self.size: int = resp["size"]
        self.url: str = resp["url"]
        self.proxy_url: str = resp["proxy_url"]
        self.height: Optional[int] = resp.get("height")
        self.width: Optional[int] = resp.get("width")
        self.ephemeral: Optional[bool] = resp.get("ephemeral")
        self.content: Optional[bytes] = None  # Filled after download is called

    def download(self) -> Union[bytes, Awaitable[bytes]]:
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
                 users: Optional[List[Snowflake.TYPING]] = None,
                 roles: Optional[List[Snowflake.TYPING]] = None,
                 replied_user: bool = False):
        self.everyone: bool = everyone
        self.users: List[Snowflake.TYPING] = users
        self.roles: List[Snowflake.TYPING] = roles
        self.replied_user: bool = replied_user

    def to_dict(self, *, reply: bool = False) -> dict:
        ret = {"parse": []}
        if self.everyone:
            ret["parse"].append("everyone")
        if self.users:
            ret["users"] = [str(x) for x in self.users]
        elif self.users is None:
            ret["parse"].append("users")
        if self.roles:
            ret["roles"] = [str(x) for x in self.roles]
        elif self.roles is None:
            ret["parse"].append("roles")
        if reply:
            ret["replied_user"] = self.replied_user
        return ret


class ListThreadsResponse:
    RESPONSE = Union["ListThreadsResponse", Awaitable["ListThreadsResponse"]]

    def __init__(self, client: "APIClient", resp: dict):
        self.threads: List[Channel] = [Channel.create(client, x) for x in resp["threads"]]
        self.members: List[ThreadMember] = [ThreadMember(client, x) for x in resp["members"]]
        self.has_more: Optional[bool] = resp.get("has_more")
