import copy
import inspect
import typing
import pathlib
import datetime

from .emoji import Emoji
from .guild import Member
from .permission import PermissionFlags, Role
from .snowflake import Snowflake
from .user import User
from ..base.model import DiscordObjectBase, TypeBase, FlagBase


class Channel(DiscordObjectBase):
    def __init__(self, client, resp, *, guild_id=None):
        super().__init__(client, resp)
        self._cache_type = "channel"
        self.type = ChannelTypes(resp["type"])
        self.guild_id = Snowflake.optional(resp.get("guild_id")) or Snowflake.ensure_snowflake(guild_id)
        self.position = resp.get("position")
        self.permission_overwrites = [Overwrite(x) for x in resp.get("permission_overwrites", [])]
        self.name = resp.get("name")
        self.topic = resp.get("topic")
        self.nsfw = resp.get("nsfw")
        self.last_message_id = Snowflake.optional(resp.get("last_message_id"))
        self.bitrate = resp.get("bitrate")
        self.user_limit = resp.get("user_limit")
        self.rate_limit_per_user = resp.get("rate_limit_per_user")
        self.recipients = resp.get("recipients", [])
        self.icon = resp.get("icon")
        self.owner_id = Snowflake.optional(resp.get("owner_id"))
        self.application_id = Snowflake.optional(resp.get("application_id"))
        self.parent_id = Snowflake.optional(resp.get("parent_id"))
        self.__last_pin_timestamp = resp.get("last_pin_timestamp")
        self.last_pin_timestamp = datetime.datetime.fromisoformat(self.__last_pin_timestamp) if self.__last_pin_timestamp else self.__last_pin_timestamp
        self.rtc_region = resp.get("rtc_region")
        self.__video_quality_mode = resp.get("video_quality_mode")
        self.video_quality_mode = VideoQualityModes(self.__video_quality_mode) if self.__video_quality_mode else self.__video_quality_mode
        self.message_count = resp.get("message_count")
        self.member_count = resp.get("member_count")
        self.thread_metadata = ThreadMetadata.optional(self.client, resp.get("thread_metadata"))
        self.member = ThreadMember.optional(self.client, resp.get("member"))

    def create_message(self, *args, **kwargs):
        if not self.is_messageable():
            raise TypeError("You can't send message in this type of channel.")
        return self.client.create_message(self, *args, **kwargs)

    @property
    def send(self):
        return self.create_message

    def modify(self, **kwargs):
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

    def bulk_delete_messages(self, *messages: typing.Union[int, str, Snowflake, "Message"]):
        return self.client.bulk_delete_messages(self, messages)

    def edit_permissions(self, overwrite):
        return self.client.edit_channel_permissions(self, overwrite)

    def request_invites(self):
        return self.client.request_channel_invites(self)

    def create_invite(self, **kwargs):
        return self.client.create_channel_invite(self, **kwargs)

    def delete_permissions(self, overwrite):
        return self.client.delete_channel_permission(self, overwrite)

    def follow(self, target_channel: typing.Union[int, str, Snowflake, "Channel"]):
        return self.client.follow_news_channel(self, target_channel)

    def trigger_typing_indicator(self):
        return self.client.trigger_typing_indicator(self)

    def request_pinned_messages(self):
        return self.client.request_pinned_messages(self)

    def add_recipient(self, user: typing.Union[int, str, Snowflake, User], access_token: str, nick: str):
        if not self.type.group_dm:
            raise AttributeError("This type of channel is not allowed to add recipient.")
        return self.client.group_dm_add_recipient(self, user, access_token, nick)

    def remove_recipient(self, user: typing.Union[int, str, Snowflake, User]):
        if not self.type.group_dm:
            raise AttributeError("This type of channel is not allowed to remove recipient.")
        return self.client.group_dm_remove_recipient(self, user)

    def start_thread(self, message: typing.Union[int, str, Snowflake, "Message"] = None, *, name: str, auto_archive_duration: int):
        return self.client.start_thread(self, message, name=name, auto_archive_duration=auto_archive_duration)

    def join_thread(self):
        if not self.is_thread_channel():
            raise AttributeError("This type of channel is not allowed to join thread.")
        return self.client.join_thread(self)

    def add_thread_member(self, user: typing.Union[int, str, Snowflake, User]):
        if not self.is_thread_channel():
            raise AttributeError("This type of channel is not allowed to add thread member.")
        return self.client.add_thread_member(user)

    def leave_thread(self):
        if not self.is_thread_channel():
            raise AttributeError("This type of channel is not allowed to leave thread.")
        return self.client.leave_thread(self)

    def remove_thread_member(self, user: typing.Union[int, str, Snowflake, User]):
        if not self.is_thread_channel():
            raise AttributeError("This type of channel is not allowed to remove thread member.")
        return self.client.remove_thread_member(self, user)

    def list_thread_members(self):
        if not self.is_thread_channel():
            raise AttributeError("This type of channel is not allowed to list thread members.")
        return self.client.list_thread_members(self)

    def list_active_threads(self):
        return self.client.list_active_threads(self)

    def list_public_archived_threads(self, *, before: typing.Union[str, datetime.datetime] = None, limit: int = None):
        return self.client.list_public_archived_threads(self, before, limit)

    def list_private_archived_threads(self, *, before: typing.Union[str, datetime.datetime] = None, limit: int = None):
        return self.client.list_private_archived_threads(self, before, limit)

    def list_joined_private_archived_threads(self, *, before: typing.Union[str, datetime.datetime] = None, limit: int = None):
        return self.client.list_joined_private_archived_threads(self, before, limit)

    @property
    def mention(self):
        return f"<#{self.id}>"

    @property
    def guild(self):
        if self.guild_id and self.client.has_cache:
            return self.client.cache.get(self.guild_id, "guild")

    def is_messageable(self):
        return self.type.guild_text or self.type.guild_news or self.type.dm or self.type.group_dm

    def is_thread_channel(self):
        return self.type.guild_news_thread or self.type.guild_public_thread or self.type.guild_private_thread


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


class Message(DiscordObjectBase):
    def __init__(self, client, resp, *, guild_id=None, webhook_token=None, interaction_token=None, original_response=False):
        from .interactions import MessageInteraction, Component  # Prevent circular import.
        super().__init__(client, resp)
        self._cache_type = "message"
        self.channel_id = Snowflake(resp["channel_id"])
        self.guild_id = Snowflake.optional(resp.get("guild_id") or guild_id)
        self.author = User.create(client, resp["author"])
        self.__member = resp.get("member")
        self.member = Member.create(self.client, self.__member, user=self.author, guild_id=self.guild_id) if self.__member else self.__member
        self.content = resp["content"]
        self.timestamp = datetime.datetime.fromisoformat(resp["timestamp"])
        self.__edited_timestamp = resp["edited_timestamp"]
        self.edited_timestamp = datetime.datetime.fromisoformat(self.__edited_timestamp) if self.__edited_timestamp else self.__edited_timestamp
        self.tts = resp["tts"]
        self.mention_everyone = resp["mention_everyone"]
        self.mentions = resp["mentions"]
        self.mention_roles = [Role(self.client, x) for x in resp["mention_roles"]]
        self.mention_channels = [ChannelMention(x) for x in resp.get("mention_channels", [])]
        self.attachments = [Attachment(self.client, x) for x in resp["attachments"] or []]
        self.embeds = [Embed.create(x) for x in resp["embeds"] or []]
        self.reactions = [Reaction(self.client, x) for x in resp.get("reactions", [])]
        self.nonce = resp.get("nonce")
        self.pinned = resp["pinned"]
        self.webhook_id = Snowflake.optional(resp.get("webhook_id"))
        self.__webhook_token = webhook_token
        self.__interaction_token = interaction_token
        self.__original_response = original_response
        self.type = MessageTypes(resp["type"])
        self.activity = MessageActivity.optional(resp.get("activity"))
        self.application = resp.get("application")
        self.message_reference = MessageReference(resp.get("message_reference", {}))
        self.__flags = resp.get("flags")
        self.flags = MessageFlags.from_value(self.__flags) if self.__flags else self.__flags
        self.stickers = [MessageSticker(x) for x in resp.get("stickers", [])]
        self.__referenced_message = resp.get("referenced_message")
        self.referenced_message = Message.create(self.client, self.__referenced_message, guild_id=self.guild_id) if self.__referenced_message else self.__referenced_message
        self.__interaction = resp.get("interaction")
        self.interaction = MessageInteraction(self.client, self.__interaction) if self.__interaction else self.__interaction
        self.__thread = resp.get("thread")
        self.thread = Channel.create(self.client, self.__thread, guild_id=self.guild_id) if self.__thread else self.__thread
        self.components = [Component.auto_detect(client, x) for x in resp.get("components", [])]

    def reply(self, content=None, **kwargs):
        kwargs["message_reference"] = self
        mention = kwargs.pop("mention") if "mention" in kwargs.keys() else True
        allowed_mentions = kwargs.get("allowed_mentions", self.client.default_allowed_mentions or AllowedMentions(replied_user=mention)).copy()
        allowed_mentions.replied_user = mention
        kwargs["allowed_mentions"] = allowed_mentions.to_dict(reply=True)
        return self.client.create_message(self.channel_id, content, **kwargs)

    def edit(self, **kwargs):
        if self.__webhook_token:
            kwargs["webhook_token"] = self.__webhook_token
            return self.client.edit_webhook_message(self.webhook_id, self, **kwargs)
        elif self.__interaction_token:
            kwargs["interaction_token"] = self.__interaction_token
            if not self.__original_response:
                kwargs["message"] = self
            return self.client.edit_interaction_response(**kwargs)
        return self.client.edit_message(self.channel_id, self.id, **kwargs)

    def delete(self):
        if self.__webhook_token:
            return self.client.delete_webhook_message(self.webhook_id, self, webhook_token=self.__webhook_token)
        elif self.__interaction_token:
            return self.client.delete_interaction_response(interaction_token=self.__interaction_token, message="@original" if self.__original_response else self)
        return self.client.delete_message(self.channel_id, self.id)

    def crosspost(self):
        return self.client.crosspost_message(self.channel_id, self.id)

    def create_reaction(self, emoji: typing.Union[Emoji, str]):
        return self.client.create_reaction(self.channel_id, self.id, emoji)

    def delete_reaction(self, emoji: typing.Union[Emoji, str], user: typing.Union[int, str, Snowflake, User] = "@me"):
        return self.client.delete_reaction(self.channel_id, self.id, emoji, user)

    def pin(self):
        return self.client.pin_message(self.channel_id, self.id)

    def unpin(self):
        return self.client.unpin_message(self.channel_id, self.id)

    def start_thread(self, *, name: str, auto_archive_duration: int):
        return self.client.start_thread(self.channel_id, name=name, auto_archive_duration=auto_archive_duration)

    @property
    def guild(self):
        if self.guild_id and self.client.has_cache:
            return self.client.get(self.guild_id, "guild")

    @property
    def channel(self):
        if self.channel_id and self.client.has_cache:
            if self.guild_id:
                return self.guild.get(self.channel_id, "channel") or self.client.get(self.channel_id, "channel")
            else:
                return self.client.get(self.channel_id, "channel")


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


class MessageActivity:
    def __init__(self, resp):
        self.type = MessageActivityTypes(resp["type"])
        self.party_id = resp.get("party_id")  # This is actually set as string in discord docs.

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


class MessageSticker:
    def __init__(self, resp):
        self.id = Snowflake(resp["id"])
        self.pack_id = Snowflake(resp["pack_id"])
        self.name = resp["name"]
        self.description = resp["description"]
        self.tags = resp.get("tags")
        self.asset = resp["asset"]
        self.format_type = MessageStickerFormatTypes(resp["format_type"])


class MessageStickerFormatTypes(TypeBase):
    PNG = 1
    APNG = 2
    LOTTIE = 3


class MessageReference:
    def __init__(self, resp):
        self.message_id = Snowflake.optional(resp.get("message_id"))
        self.channel_id = Snowflake.optional(resp.get("channel_id"))
        self.guild_id = Snowflake.optional(resp.get("guild_id"))
        self.fail_if_not_exists = resp.get("fail_if_not_exists", True)

    def to_dict(self):
        return {"message_id": str(self.message_id),
                "channel_id": str(self.channel_id),
                "guild_id": str(self.guild_id),
                "fail_if_not_exists": self.fail_if_not_exists}

    @classmethod
    def from_message(cls, message: Message, fail_if_not_exists: bool = True):
        return cls({"message_id": message.id, "channel_id": message.channel_id, "guild_id": message.guild_id, "fail_if_not_exists": fail_if_not_exists})

    @classmethod
    def from_id(cls, **kwargs):
        return cls(kwargs)


class FollowedChannel:
    def __init__(self, client, resp):
        self.client = client
        self.channel_id = Snowflake(resp["channel_id"])
        self.webhook_id = Snowflake(resp["webhook_id"])

    @property
    def channel(self):
        if self.client.has_cache:
            return self.client.get(self.channel_id)


class Reaction:
    def __init__(self, client, resp):
        self.count = resp["count"]
        self.me = resp["me"]
        self.emoji = Emoji(client, resp["emoji"])


class Overwrite:
    def __init__(self, resp):
        self.id = Snowflake(resp["id"])
        self.type = resp["type"]
        self.allow = PermissionFlags.from_value(int(resp["allow"]))
        self.deny = PermissionFlags.from_value(int(resp["deny"]))

    def to_dict(self):
        return {"id": str(self.id), "type": self.type, "allow": str(int(self.allow)), "deny": str(int(self.deny))}

    def edit(self, **kwargs):
        for k, v in kwargs.items():
            self.allow.__setattr__(k, v)
            self.deny.__setattr__(k, not v)

    @classmethod
    def create(cls,
               user: typing.Union[str, int, Snowflake, User] = None,
               role: typing.Union[str, int, Snowflake, Role] = None,
               allow: typing.Union[int, PermissionFlags] = 0,
               deny: typing.Union[int, PermissionFlags] = 0):
        if user is None and role is None:
            raise TypeError("you must pass user or role.")
        return cls(dict(id=int(user or role), type=0 if role else 1, allow=allow, deny=deny))


class ThreadMetadata:
    def __init__(self, client, resp):
        self.client = client
        self.archived = resp["archived"]
        self.archiver_id = Snowflake.optional(resp.get("archiver_id"))
        self.auto_archive_duration = resp["auto_archive_duration"]
        self.archive_timestamp = datetime.datetime.fromisoformat(resp["archive_timestamp"])
        self.locked = resp.get("locked", False)

    @property
    def archiver(self):
        if self.client.has_cache and self.archiver_id:
            return self.client.get(self.archiver_id)

    @classmethod
    def optional(cls, client, resp):
        if resp:
            return cls(client, resp)


class ThreadMember:
    def __init__(self, client, resp):
        self.client = client
        self.id = Snowflake(resp["id"])
        self.user_id = Snowflake(resp["user_id"])
        self.join_timestamp = datetime.datetime.fromisoformat(resp["join_timestamp"])
        self.flags = resp["flags"]

    @property
    def user(self):
        if self.client.has_cache:
            return self.client.get(self.user_id, "user")

    @classmethod
    def optional(cls, client, resp):
        if resp:
            return cls(client, resp)


class Embed:
    def __init__(self, *, title: str = None, description: str = None, url: str = None, timestamp: datetime.datetime = None, color: int = None, **kwargs):
        resp = self.__create(title=title, description=description, url=url, timestamp=timestamp, color=color)
        resp.update(kwargs)
        self.title = resp.get("title")
        self.type = resp.get("type", "rich")
        self.description = resp.get("description")
        self.url = resp.get("url")
        self.__timestamp = resp.get("timestamp")
        self.timestamp = datetime.datetime.fromisoformat(self.__timestamp) if self.__timestamp else self.__timestamp
        self.color = resp.get("color")
        self.footer = EmbedFooter.optional(resp.get("footer"))
        self.image = EmbedImage.optional(resp.get("image"))
        self.thumbnail = EmbedThumbnail.optional(resp.get("thumbnail"))
        self.video = EmbedVideo.optional(resp.get("video"))
        self.provider = EmbedProvider.optional(resp.get("provider"))
        self.author = EmbedAuthor.optional(resp.get("author"))
        self.fields = [EmbedField(x) for x in resp.get("fields", [])]

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

    def to_dict(self):
        ret = {}
        if self.title:
            ret["title"] = self.title
        if self.type:
            ret["type"] = self.type
        if self.description:
            ret["description"] = self.description
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


class EmbedThumbnail:
    def __init__(self, resp):
        self.url = resp.get("url")
        self.proxy_url = resp.get("proxy_url")
        self.height = resp.get("height")
        self.width = resp.get("width")

    def to_dict(self):
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


class EmbedVideo:
    def __init__(self, resp):
        self.url = resp.get("url")
        self.proxy_url = resp.get("proxy_url")
        self.height = resp.get("height")
        self.width = resp.get("width")

    def to_dict(self):
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


class EmbedImage:
    def __init__(self, resp):
        self.url = resp.get("url")
        self.proxy_url = resp.get("proxy_url")
        self.height = resp.get("height")
        self.width = resp.get("width")

    def to_dict(self):
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


class EmbedProvider:
    def __init__(self, resp):
        self.name = resp.get("name")
        self.url = resp.get("url")

    def to_dict(self):
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


class EmbedAuthor:
    def __init__(self, resp):
        self.name = resp.get("name")
        self.url = resp.get("url")
        self.icon_url = resp.get("icon_url")
        self.proxy_icon_url = resp.get("proxy_icon_url")

    def to_dict(self):
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


class EmbedFooter:
    def __init__(self, resp):
        self.text = resp["text"]
        self.icon_url = resp.get("icon_url")
        self.proxy_icon_url = resp.get("proxy_icon_url")

    def to_dict(self):
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


class EmbedField:
    def __init__(self, resp):
        self.name = resp["name"]
        self.value = resp["value"]
        self.inline = resp.get("inline", True)

    def to_dict(self):
        return {"name": self.name, "value": self.value, "inline": self.inline}

    @classmethod
    def optional(cls, resp):
        if resp:
            return cls(resp)


class Attachment:
    def __init__(self, client, resp):
        self.client = client
        self.id = Snowflake(resp["id"])
        self.filename = resp["filename"]
        self.content_type = resp.get("content_type")
        self.size = resp["size"]
        self.url = resp["url"]
        self.proxy_url = resp["proxy_url"]
        self.height = resp.get("height")
        self.width = resp.get("width")
        self.content = None  # Filled after download is called

    def download(self):
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

    def to_dict(self):
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
    def __init__(self, resp):
        self.id = Snowflake(resp["id"])
        self.guild_id = Snowflake(resp["guild_id"])
        self.type = ChannelTypes(resp["type"])
        self.name = resp["name"]


class AllowedMentions:
    def __init__(self, *,
                 everyone: bool = False,
                 users: typing.List[typing.Union[str, int, Snowflake]] = None,
                 roles: typing.List[typing.Union[str, int, Snowflake]] = None,
                 replied_user: bool = False):
        self.everyone: bool = everyone
        self.users = users or []
        self.roles = roles or []
        self.replied_user = replied_user

    def to_dict(self, *, reply: bool = False):
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

    def copy(self):
        return copy.copy(self)


class ListThreadsResponse:
    def __init__(self, client, resp):
        self.threads = [Channel.create(client, x) for x in resp["threads"]]
        self.members = [ThreadMember(client, x) for x in resp["members"]]
        self.has_more = resp["has_more"]
