import datetime


class Channel:
    def __init__(self, resp):
        self.id = resp["id"]
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


class Message:
    def __init__(self, resp):
        self.id = resp["id"]
        self.channel_id = resp["channel_id"]
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
        self.message_reference = resp.get("message_reference")
        self.flags = resp.get("flags")
        self.stickers = resp.get("stickers", [])
        self.referenced_message = resp.get("referenced_message")
        self.interaction = resp.get("interaction")

        self.edited_timestamp = datetime.datetime.fromisoformat(self.__edited_timestamp) if self.__edited_timestamp else self.__edited_timestamp
