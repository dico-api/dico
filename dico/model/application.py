import typing

from ..base.model import FlagBase, TypeBase
from ..utils import cdn_url
from .snowflake import Snowflake
from .user import User

if typing.TYPE_CHECKING:
    from ..api import APIClient


class Application:
    TYPING = typing.Union[int, str, Snowflake, "Application"]
    RESPONSE = typing.Union["Application", typing.Awaitable["Application"]]

    def __init__(self, client: "APIClient", resp: dict):
        self.client: "APIClient" = client
        self.id: typing.Optional[Snowflake] = Snowflake.optional(resp.get("id"))
        self.name: typing.Optional[str] = resp.get("name")
        self.icon: typing.Optional[str] = resp.get("icon")
        self.description: typing.Optional[str] = resp.get("description")
        self.rpc_origins: typing.Optional[typing.List[str]] = resp.get("rpc_origins")
        self.bot_public: typing.Optional[bool] = resp.get("bot_public")
        self.bot_require_code_grant: typing.Optional[bool] = resp.get(
            "bot_require_code_grant"
        )
        self.terms_of_service_url: typing.Optional[str] = resp.get(
            "terms_of_service_url"
        )
        self.privacy_policy_url: typing.Optional[str] = resp.get("privacy_policy_url")
        self.__owner = resp.get("owner")
        self.owner: typing.Optional[User] = (
            User.create(client, self.__owner) if self.__owner else self.__owner
        )
        self.summary: typing.Optional[str] = resp.get("summary")
        self.verify_key: typing.Optional[str] = resp.get("verify_key")
        self.__team = resp.get("team")
        self.team: typing.Optional[Team] = (
            Team(client, self.__team) if self.__team else self.__team
        )
        self.guild_id: typing.Optional[Snowflake] = Snowflake.optional(
            resp.get("guild_id")
        )
        self.primary_sku_id: typing.Optional[Snowflake] = Snowflake.optional(
            resp.get("primary_sku_id")
        )
        self.slug: typing.Optional[str] = resp.get("slug")
        self.cover_image: typing.Optional[str] = resp.get("cover_image")
        self.__flags = resp.get("flags")
        self.flags: typing.Optional[ApplicationFlags] = (
            ApplicationFlags.from_value(self.__flags)
            if self.__flags is not None
            else self.__flags
        )
        self.tags: typing.Optional[typing.List[str]] = resp.get("tags")
        self.__install_params = resp.get("install_params")
        self.install_params: typing.Optional[
            InstallParams
        ] = self.__install_params and InstallParams(self.__install_params)
        self.custom_install_url: typing.Optional[str] = resp.get("custom_install_url")
        self.role_connections_verification_url: typing.Optional[str] = resp.get(
            "role_connections_verification_url"
        )

        self.client.application = self
        self.client.application_id = self.id

    def __int__(self) -> int:
        return int(self.id)

    def __str__(self) -> str:
        return self.name

    def icon_url(
        self, *, extension: str = "webp", size: int = 1024
    ) -> typing.Optional[str]:
        if self.icon:
            return cdn_url(
                "app-icons/{application_id}",
                image_hash=self.icon,
                extension=extension,
                size=size,
                application_id=self.id,
            )

    def cover_image_url(
        self, *, extension: str = "webp", size: int = 1024
    ) -> typing.Optional[str]:
        if self.cover_image:
            return cdn_url(
                "app-icons/{application_id}",
                image_hash=self.cover_image,
                extension=extension,
                size=size,
                application_id=self.id,
            )

    @property
    def owner_ids(self) -> typing.List[Snowflake]:
        if self.team:
            return self.team.member_ids
        elif self.owner:
            return [self.owner.id]
        return []


class ApplicationFlags(FlagBase):
    GATEWAY_PRESENCE = 1 << 12
    GATEWAY_PRESENCE_LIMITED = 1 << 13
    GATEWAY_GUILD_MEMBERS = 1 << 14
    GATEWAY_GUILD_MEMBERS_LIMITED = 1 << 15
    VERIFICATION_PENDING_GUILD_LIMIT = 1 << 16
    EMBEDDED = 1 << 17
    GATEWAY_MESSAGE_CONTENT = 1 << 18
    GATEWAY_MESSAGE_CONTENT_LIMITED = 1 << 19
    APPLICATION_COMMAND_BADGE = 1 << 23


class InstallParams:
    def __init__(self, resp: dict):
        self.scopes: typing.List[str] = resp["scopes"]
        self.permissions: str = resp["permissions"]


class Team:
    def __init__(self, client: "APIClient", resp: dict):
        self.icon: typing.Optional[str] = resp["icon"]
        self.id: Snowflake = Snowflake(resp["id"])
        self.members: typing.List[TeamMember] = [
            TeamMember(client, x) for x in resp["members"]
        ]
        self.name: str = resp["name"]
        self.owner_user_id: Snowflake = Snowflake(resp["owner_user_id"])

    def icon_url(
        self, *, extension: str = "webp", size: int = 1024
    ) -> typing.Optional[str]:
        if self.icon:
            return cdn_url(
                "team-icons/{team_id}",
                image_hash=self.icon,
                extension=extension,
                size=size,
                team_id=self.id,
            )

    @property
    def member_ids(self) -> typing.List[Snowflake]:
        return [x.user.id for x in self.members]


class TeamMember:
    def __init__(self, client: "APIClient", resp: dict):
        self.membership_state: MembershipState = MembershipState(
            resp["membership_state"]
        )
        self.permissions: typing.List[str] = resp["permissions"]
        self.team_id: Snowflake = Snowflake(resp["team_id"])
        self.user: User = User.create(client, resp["user"])


class MembershipState(TypeBase):
    INVITED = 1
    ACCEPTED = 2
