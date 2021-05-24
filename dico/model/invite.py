import datetime
from .channel import Channel
from .guild import Guild
from .user import User
from ..base.model import TypeBase


class Invite:
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
