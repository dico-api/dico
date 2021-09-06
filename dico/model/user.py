import typing
from .snowflake import Snowflake
from ..base.model import DiscordObjectBase, FlagBase, TypeBase
from ..utils import cdn_url

if typing.TYPE_CHECKING:
    from .channel import Channel
    from .voice import VoiceState


class User(DiscordObjectBase):
    TYPING = typing.Union[int, str, Snowflake, "User"]
    RESPONSE = typing.Union["User", typing.Awaitable["User"]]
    RESPONSE_AS_LIST = typing.Union[typing.List["User"], typing.Awaitable[typing.List["User"]]]
    _cache_type = "user"

    def __init__(self, client, resp):
        super().__init__(client, resp)
        self.username: typing.Optional[str] = resp.get("username")
        self.discriminator: typing.Optional[str] = resp.get("discriminator")
        self.avatar: typing.Optional[str] = resp.get("avatar")
        self.bot: typing.Optional[bool] = resp.get("bot")
        self.system: typing.Optional[bool] = resp.get("system")
        self.mfa_enabled: typing.Optional[bool] = resp.get("mfa_enabled")
        self.banner: typing.Optional[str] = resp.get("banner")
        self.accent_color: typing.Optional[int] = resp.get("accent_color")
        self.locale: typing.Optional[str] = resp.get("locale")
        self.verified: typing.Optional[bool] = resp.get("verified")
        self.email: typing.Optional[str] = resp.get("email")
        self.flags: UserFlags = UserFlags.from_value(resp.get("flags", 0))
        self.premium_type: PremiumTypes = PremiumTypes(resp.get("premium_type", 0))
        self.public_flags: UserFlags = UserFlags.from_value(resp.get("public_flags", 0))

        self.voice_state: typing.Optional["VoiceState"] = self.raw.get("voice_state")  # Filled later.
        self.dm_channel_id: typing.Optional[Snowflake] = None

    def __str__(self):
        return f"{self.username}#{self.discriminator}"

    @property
    def mention(self) -> str:
        return f"<@{self.id}>"

    def avatar_url(self, *, extension="webp", size=1024) -> str:
        if self.avatar:
            return cdn_url("avatars/{user_id}", image_hash=self.avatar, extension=extension, size=size, user_id=self.id)
        else:
            return cdn_url("embed/avatars", image_hash=self.discriminator % 5, extension=extension)

    def banner_url(self, *, extension="webp", size=1024) -> typing.Optional[str]:
        if self.banner:
            return cdn_url("banners/{user_id}", image_hash=self.banner, extension=extension, size=size, user_id=self.id)

    def set_voice_state(self, voice_state):
        self.voice_state = voice_state
        self.raw["voice_state"] = voice_state

    def get_voice_state(self) -> "VoiceState":
        return self.voice_state

    def create_dm(self) -> "Channel.RESPONSE":
        from .channel import Channel
        channel = self.client.create_dm(self)
        if isinstance(channel, Channel):
            self.dm_channel_id = channel.id
            return channel
        else:
            return self.__async_assign_dm(channel)

    async def __async_assign_dm(self, channel):
        channel = await channel
        self.dm_channel_id = channel.id
        return channel

    def create_message(self, *args, **kwargs):
        if self.dm_channel_id is None:
            from .channel import Channel
            channel = self.create_dm()
            if not isinstance(channel, Channel):
                return self.__async_create_message(channel, *args, **kwargs)
            self.dm_channel_id = channel.id
        return self.client.create_message(self.dm_channel_id, *args, **kwargs)

    async def __async_create_message(self, req, *args, **kwargs):
        await req
        return await self.client.create_message(self.dm_channel_id, *args, **kwargs)

    @property
    def send(self):
        return self.create_message


class UserFlags(FlagBase):
    NONE = 0
    DISCORD_EMPLOYEE = 1 << 0
    PARTNERED_SERVER_OWNER = 1 << 1
    HYPESQUAD_EVENTS = 1 << 2
    BHG_HUNTER_LEVEL_1 = 1 << 3
    HOUSE_BRAVERY = 1 << 6
    HOUSE_BRILLIANCE = 1 << 7
    HOUSE_BALANCE = 1 << 8
    EARLY_SUPPORTER = 1 << 9
    TEAM_USER = 1 << 10
    BHG_HUNTER_LEVEL_2 = 1 << 14
    VERIFIED_BOT = 1 << 16
    EARLY_VERIFIED_BOT_DEVELOPER = 1 << 17
    DISCORD_CERTIFIED_MODERATOR = 1 << 18


class PremiumTypes(TypeBase):
    NONE = 0
    NITRO_CLASSIC = 1
    NITRO = 2
