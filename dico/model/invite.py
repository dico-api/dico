import typing
import datetime
from .channel import Channel
from .guild import Guild, GuildMember
from .user import User
from ..base.model import TypeBase


class Invite:
    RESPONSE = typing.Union["Invite", typing.Awaitable["Invite"]]
    RESPONSE_AS_LIST = typing.Union[typing.List["Invite"], typing.Awaitable[typing.List["Invite"]]]

    def __init__(self, client, resp):
        self.client = client
        self.code = resp["code"]
        self.__guild = resp.get("guild")
        self.guild = Guild.create(client, self.__guild) if self.__guild else self.__guild
        self.channel = Channel.create(client, resp["channel"])
        self.__inviter = resp.get("inviter")
        self.inviter = User.create(client, self.__inviter) if self.__inviter else self.__inviter
        self.__target_type = resp.get("target_type")
        self.target_type = InviteTargetTypes(self.__target_type) if self.__target_type else self.__target_type
        self.target_application = resp.get("target_application")
        self.approximate_presence_count = resp.get("approximate_presence_count")
        self.approximate_member_count = resp.get("approximate_member_count")
        self.__expires_at = resp.get("expires_at")
        self.expires_at = datetime.datetime.fromisoformat(self.__expires_at) if self.__expires_at else self.__expires_at
        self.__stage_instance = resp.get("stage_instance")
        self.stage_instance = InviteStageInstance(client, self.__stage_instance) if self.__stage_instance else self.__stage_instance
        self.metadata = InviteMetadata.optional(resp)

    def __str__(self):
        return self.code

    def delete(self, *, reason: str = None):
        return self.client.delete_invite(self.code, reason=reason)

    @property
    def url(self):
        return f"https://discord.gg/{self.code}"


class InviteTargetTypes(TypeBase):
    STREAM = 1
    EMBEDDED_APPLICATION = 2


class InviteMetadata:
    def __init__(self, resp):
        self.uses = resp["uses"]
        self.max_uses = resp["max_uses"]
        self.max_age = resp["max_age"]
        self.temporary = resp["temporary"]
        self.created_at = datetime.datetime.fromisoformat(resp["created_at"])

    @classmethod
    def optional(cls, resp):
        if "uses" in resp:
            return cls(resp)


class InviteStageInstance:
    def __init__(self, client, resp):
        self.members = [GuildMember.create(client, x) for x in resp["members"]]
        self.participant_count = resp["participant_count"]
        self.speaker_count = resp["speaker_count"]
        self.topic = resp["topic"]
