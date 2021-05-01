import copy
import typing
import datetime

from .guild import Member
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
        self.permission_overwrites = resp.get("permission_overwrites", [])
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
        self.rtc_region = resp.get("rtc_region")
        self.video_quality_mode = resp.get("video_quality_mode")

        self.last_pin_timestamp = datetime.datetime.fromisoformat(self.__last_pin_timestamp) if self.__last_pin_timestamp else self.__last_pin_timestamp

    @property
    def create_message(self):
        if self.is_store_channel() or self.is_guild_voice_channel() or self.is_channel_category():
            raise TypeError("You can't send message in this type of channel.")
        return self.client.create_message

    @property
    def mention(self):
        return f"<#{self.id}>"

    @property
    def guild(self):
        if self.guild_id:
            return self.client.cache.get_guild(self.guild_id)

    def is_guild_text_channel(self):
        return self.type.guild_text

    def is_guild_news_channel(self):
        return self.type.guild_news

    def is_guild_voice_channel(self):
        return self.type.guild_voice

    def is_dm_channel(self):
        return self.type.dm

    def is_group_dm_channel(self):
        return self.type.group_dm

    def is_channel_category(self):
        return self.type.guild_category

    def is_store_channel(self):
        return self.type.guild_store

    def is_stage_channel(self):
        return self.type.guild_stage_voice


class ChannelTypes(TypeBase):
    GUILD_TEXT = 0
    DM = 1
    GUILD_VOICE = 2
    GROUP_DM = 3
    GUILD_CATEGORY = 4
    GUILD_NEWS = 5
    GUILD_STORE = 6
    GUILD_STAGE_VOICE = 13


class VideoQualityModes:
    AUTO = 1
    FULL = 2


class Message(DiscordObjectBase):
    def __init__(self, client, resp, *, guild_id=None):
        super().__init__(client, resp)
        self._cache_type = "message"
        self.channel_id = Snowflake(resp["channel_id"])
        self.guild_id = Snowflake.optional(resp.get("guild_id") or guild_id)
        self.author = User.create(client, resp["author"])
        self.__member = resp.get("member")
        self.content = resp["content"]
        self.timestamp = datetime.datetime.fromisoformat(resp["timestamp"])
        self.__edited_timestamp = resp["edited_timestamp"]
        self.tts = resp["tts"]
        self.mention_everyone = resp["mention_everyone"]
        self.mentions = resp["mentions"]
        self.mention_channels = resp.get("mention_channels", [])
        self.attachments = resp["attachments"] or []
        self.embeds = resp["embeds"] or []
        self.reactions = resp.get("reactions", [])
        self.nonce = resp.get("nonce")
        self.pinned = resp["pinned"]
        self.webhook_id = Snowflake.optional(resp.get("webhook_id"))
        self.type = MessageTypes(resp["type"])
        self.activity = MessageActivity.optional(resp.get("activity"))
        self.application = resp.get("application")
        self.message_reference = MessageReference(resp.get("message_reference", {}))
        self.__flags = resp.get("flags")
        self.stickers = [MessageSticker(x) for x in resp.get("stickers", [])]
        self.__referenced_message = resp.get("referenced_message")
        self.interaction = resp.get("interaction")

        self.edited_timestamp = datetime.datetime.fromisoformat(self.__edited_timestamp) if self.__edited_timestamp else self.__edited_timestamp

        if self.__member:
            self.member = Member(self.client, self.__member, user=self.author)

        if self.__referenced_message:
            self.referenced_message = Message.create(self.client, self.__referenced_message, guild_id=self.guild_id)

        if self.__flags:
            self.flags = MessageFlags(self.__flags)

    def reply(self, content, **kwargs):
        kwargs["message_reference"] = self
        mention = kwargs.pop("mention") if "mention" in kwargs.keys() else True
        allowed_mentions = kwargs.get("allowed_mentions", self.client.default_allowed_mentions or AllowedMentions(replied_user=mention)).copy()
        allowed_mentions.replied_user = mention
        kwargs["allowed_mentions"] = allowed_mentions.to_dict(reply=True)
        return self.client.create_message(self.channel_id, content, **kwargs)

    @property
    def guild(self):
        if self.guild_id:
            return self.client.get_guild(self.guild_id)

    @property
    def channel(self):
        if self.channel_id:
            if self.guild_id:
                return self.guild.get_channel(self.channel_id) or self.client.get_channel(self.channel_id)
            else:
                return self.client.get_channel(self.channel_id)


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
