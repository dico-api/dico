from typing import List, Optional, Union, Awaitable

from ..base.model import TypeBase
from .snowflake import Snowflake


class AutoModerationRule:
    RESPONSE = Union["AutoModerationRule", Awaitable["AutoModerationRule"]]
    RESPONSE_AS_LIST = Union[
        List["ApplicationRoleConnectionMetadata"],
        Awaitable[List["ApplicationRoleConnectionMetadata"]],
    ]

    def __init__(self, resp: dict):
        self.id: Snowflake = Snowflake(resp["id"])
        self.guild_id: Snowflake = Snowflake(resp["guild_id"])
        self.name: str = resp["name"]
        self.creator_id: Snowflake = Snowflake(resp["creator_id"])
        self.event_type: AutoModerationEventTypes = AutoModerationEventTypes(
            resp["event_type"]
        )
        self.trigger_type: TriggerTypes = TriggerTypes(resp["trigger_type"])
        self.trigger_metadata: TriggerMetadata = TriggerMetadata(
            resp["trigger_metadata"]
        )
        self.actions: List[AutoModerationAction] = [
            AutoModerationAction(x) for x in resp["actions"]
        ]
        self.enabled: bool = resp["enabled"]
        self.exempt_roles: List[Snowflake] = [
            Snowflake(x) for x in resp["exempt_roles"]
        ]
        self.exempt_channels: List[Snowflake] = [
            Snowflake(x) for x in resp["exempt_channels"]
        ]


class TriggerTypes(TypeBase):
    KEYWORD = 1
    SPAM = 3
    KEYWORD_PRESET = 4
    MENTION_SPAM = 5


class TriggerMetadata:
    def __init__(self, resp: dict):
        self.keyword_filter: Optional[List[str]] = resp.get("keyword_filter")
        self.regex_patterns: Optional[List[str]] = resp.get("regex_patterns")
        __presets = resp.get("presets")
        self.presets: Optional[List] = __presets or [
            KeywordPresetTypes(x) for x in __presets
        ]
        self.allow_list: Optional[List[str]] = resp.get("allow_list")
        self.mention_total_limit: Optional[int] = resp.get("mention_total_limit")
        self.mention_raid_protection_enabled: Optional[bool] = resp.get(
            "mention_raid_protection_enabled"
        )


class KeywordPresetTypes(TypeBase):
    PROFANITY = 1
    SEXUAL_CONTENT = 2
    SLURS = 3


class AutoModerationEventTypes(TypeBase):
    MESSAGE_SEND = 1


class AutoModerationAction:
    def __init__(self, resp: dict):
        self.type: ActionTypes = ActionTypes(resp["type"])
        self.metadata: Optional[ActionMetadata] = ActionMetadata(resp["metadata"])


class ActionTypes(TypeBase):
    BLOCK_MESSAGE = 1
    SEND_ALERT_MESSAGE = 2
    TIMEOUT = 3


class ActionMetadata:
    def __init__(self, resp: dict):
        self.channel_id: Optional[Snowflake] = Snowflake.optional(
            resp.get("channel_id")
        )
        self.duration_second: Optional[int] = resp.get("duration_second")
        self.custom_message: Optional[str] = resp.get("custom_message")
