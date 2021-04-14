class Channel:
    def __init__(self, payload):
        self.id = payload["id"]
        self.type = payload["type"]
        self.guild_id = payload.get("guild_id")
        self.position = payload.get("position")
        self.permission_overwrites = payload.get("permission_overwrites", [])
        self.name = payload.get("name")
        self.topic = payload.get("topic")
        self.nsfw = payload.get("nsfw")
        self.last_message_id = payload.get("last_message_id")
        self.bitrate = payload.get("bitrate")
        self.user_limit = payload.get("user_limit")
        self.rate_limit_per_user = payload.get("rate_limit_per_user")
        self.recipients = payload.get("recipients", [])
        self.icon = payload.get("icon")
        self.owner_id = payload.get("owner_id")
        self.application_id = payload.get("application_id")
        self.parent_id = payload.get("parent_id")
        self.last_pin_timestamp = payload.get("last_pin_timestamp")
        self.rtc_region = payload.get("rtc_region")
        self.video_quality_mode = payload.get("video_quality_mode")


class Message:
    def __init__(self, payload):
        self.id = payload["id"]
        self.channel_id = payload["channel_id"]
        self.guild_id = payload.get("guild_id")
        self.author = payload["author"]
        self.member = payload.get("member")
        self.content = payload["content"]
        self.timestamp = payload["timestamp"]
        self.edited_timestamp = payload["edited_timestamp"]
        self.tts = payload["tts"]
        self.mention_everyone = payload["mention_everyone"]
        self.mentions = payload["mentions"]
        self.mention_channels = payload.get("mention_channels", [])
        self.attachments = payload["attachments"] or []
        self.embeds = payload["embeds"] or []
        self.reactions = payload.get("reactions", [])
        self.nonce = payload.get("nonce")
        self.pinned = payload["pinned"]
        self.webhook_id = payload.get("webhook_id")
        self.type = payload["type"]
        self.activity = payload.get("activity")
        self.application = payload.get("application")
        self.message_reference = payload.get("message_reference")
        self.flags = payload.get("flags")
        self.stickers = payload.get("stickers", [])
        self.referenced_message = payload.get("referenced_message")
        self.interaction = payload.get("interaction")
