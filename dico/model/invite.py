import typing
import datetime
from .application import Application
from .channel import Channel
from .guild import Guild, GuildMember
from .user import User
from ..base.model import TypeBase

if typing.TYPE_CHECKING:
    from ..api import APIClient


class Invite:
    RESPONSE = typing.Union["Invite", typing.Awaitable["Invite"]]
    RESPONSE_AS_LIST = typing.Union[typing.List["Invite"], typing.Awaitable[typing.List["Invite"]]]

    def __init__(self, client: "APIClient", resp: dict):
        self.client: "APIClient" = client
        self.code: str = resp["code"]
        self.__guild = resp.get("guild")
        self.guild: typing.Optional[Guild] = Guild.create(client, self.__guild) if self.__guild else self.__guild
        self.channel: Channel = Channel.create(client, resp["channel"])
        self.__inviter = resp.get("inviter")
        self.inviter: typing.Optional[User] = User.create(client, self.__inviter) if self.__inviter else self.__inviter
        self.__target_type = resp.get("target_type")
        self.target_type: typing.Optional[InviteTargetTypes] = InviteTargetTypes(self.__target_type) if self.__target_type else self.__target_type
        self.__target_application = resp.get("target_application")
        self.target_application: typing.Optional[Application] = Application(client, self.__target_application) if self.__target_application else self.__target_application
        self.approximate_presence_count: int = resp.get("approximate_presence_count")
        self.approximate_member_count: int = resp.get("approximate_member_count")
        self.__expires_at = resp.get("expires_at")
        self.expires_at: typing.Optional[datetime.datetime] = datetime.datetime.fromisoformat(self.__expires_at) if self.__expires_at else self.__expires_at
        self.__stage_instance = resp.get("stage_instance")
        self.stage_instance: typing.Optional[InviteStageInstance] = InviteStageInstance(client, self.__stage_instance) if self.__stage_instance else self.__stage_instance
        self.metadata: InviteMetadata = InviteMetadata.optional(resp)

    def __str__(self) -> str:
        return self.code

    def delete(self, *, reason: str = None) -> "Invite.RESPONSE":
        return self.client.delete_invite(self.code, reason=reason)

    @property
    def url(self) -> str:
        return f"https://discord.gg/{self.code}"

    def __repr__(self):
        return f"<{self.__class__.__name__} code={self.code}>"


class InviteTargetTypes(TypeBase):
    STREAM = 1
    EMBEDDED_APPLICATION = 2


class InviteMetadata:
    def __init__(self, resp: dict):
        self.uses: int = resp["uses"]
        self.max_uses: int = resp["max_uses"]
        self.max_age: int = resp["max_age"]
        self.temporary: bool = resp["temporary"]
        self.created_at: datetime.datetime = datetime.datetime.fromisoformat(resp["created_at"])

    @classmethod
    def optional(cls, resp):
        if "uses" in resp:
            return cls(resp)


class InviteStageInstance:
    def __init__(self, client: "APIClient", resp: dict):
        self.members: typing.List[GuildMember] = [GuildMember.create(client, x) for x in resp["members"]]
        self.participant_count: int = resp["participant_count"]
        self.speaker_count: int = resp["speaker_count"]
        self.topic: str = resp["topic"]
