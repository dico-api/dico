import copy
import typing
import datetime

from .snowflake import Snowflake
from ..base.model import DiscordObjectBase


class Channel(DiscordObjectBase):
    def __init__(self, client, resp):
        super().__init__(client, resp)
        self.type = resp["type"]
        self.guild_id = resp.get("guild_id")
        self.position = resp.get("position")
        self.permission_overwrites = resp.get("permission_overwrites", [])
        self.name = resp.get("name")
        self.topic = resp.get("topic")
        self.nsfw = resp.get("nsfw")
        self.last_message_id = resp.get("last_message_id")
        self.bitrate = resp.get("bitrate")
        self.user_limit = resp.get("user_limit")
        self.rate_limit_per_user = resp.get("rate_limit_per_user")
        self.recipients = resp.get("recipients", [])
        self.icon = resp.get("icon")
        self.owner_id = resp.get("owner_id")
        self.application_id = resp.get("application_id")
        self.parent_id = resp.get("parent_id")
        self.__last_pin_timestamp = resp.get("last_pin_timestamp")
        self.rtc_region = resp.get("rtc_region")
        self.video_quality_mode = resp.get("video_quality_mode")

        self.last_pin_timestamp = datetime.datetime.fromisoformat(self.__last_pin_timestamp) if self.__last_pin_timestamp else self.__last_pin_timestamp

        if self.guild_id:
            self.guild_id = Snowflake(self.guild_id)
        if self.last_message_id:
            self.last_message_id = Snowflake(self.last_message_id)
        if self.owner_id:
            self.owner_id = Snowflake(self.owner_id)
        if self.application_id:
            self.application_id = Snowflake(self.application_id)
        if self.parent_id:
            self.parent_id = Snowflake(self.parent_id)

    @property
    def create_message(self):
        return self.client.create_message

    @property
    def mention(self):
        return f"<#{self.id}>"


class Message(DiscordObjectBase):
    def __init__(self, client, resp):
        super().__init__(client, resp)
        self.channel_id = Snowflake(resp["channel_id"])
        self.guild_id = resp.get("guild_id")
        self.author = resp["author"]
        self.member = resp.get("member")
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
        self.webhook_id = resp.get("webhook_id")
        self.type = resp["type"]
        self.activity = resp.get("activity")
        self.application = resp.get("application")
        self.message_reference = MessageReference(resp.get("message_reference", {}))
        self.flags = resp.get("flags")
        self.stickers = resp.get("stickers", [])
        self.referenced_message = resp.get("referenced_message")
        self.interaction = resp.get("interaction")

        self.edited_timestamp = datetime.datetime.fromisoformat(self.__edited_timestamp) if self.__edited_timestamp else self.__edited_timestamp

        if self.message_reference.message_id:
            self.referenced_message = Message(self.client, self.referenced_message)

        if self.guild_id:
            self.guild_id = Snowflake(self.guild_id)
        if self.webhook_id:
            self.guild_id = Snowflake(self.webhook_id)

    def reply(self, content, **kwargs):
        kwargs["message_reference"] = self
        mention = kwargs.pop("mention") if "mention" in kwargs.keys() else True
        allowed_mentions = kwargs.get("allowed_mentions", self.client.default_allowed_mentions or AllowedMentions(replied_user=mention)).copy()
        allowed_mentions.replied_user = mention
        kwargs["allowed_mentions"] = allowed_mentions.to_dict(reply=True)
        return self.client.create_message(self.channel_id, content, **kwargs)


class MessageReference:
    def __init__(self, resp):
        self.message_id = resp.get("message_id")
        self.channel_id = resp.get("channel_id")
        self.guild_id = resp.get("guild_id")
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
            ret["users"] = self.users
        if self.roles:
            ret["parsed"].append("roles")
            ret["roles"] = self.roles
        if reply:
            ret["replied_user"] = self.replied_user
        return ret

    def copy(self):
        return copy.copy(self)
