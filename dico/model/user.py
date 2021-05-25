from ..base.model import DiscordObjectBase, FlagBase, TypeBase
from ..utils import cdn_url


class User(DiscordObjectBase):
    def __init__(self, client, resp):
        super().__init__(client, resp)
        self._cache_type = "user"
        self.username = resp.get("username")
        self.discriminator = resp.get("discriminator")
        self.avatar = resp.get("avatar")
        self.bot = resp.get("bot", False)
        self.system = resp.get("system", False)
        self.mfa_enabled = resp.get("mfa_enabled", False)
        self.locale = resp.get("locale")
        self.verified = resp.get("verified", False)
        self.email = resp.get("email")
        self.flags = UserFlags.from_value(resp.get("flags", 0))
        self.premium_type = PremiumTypes(resp.get("premium_type", 0))
        self.public_flags = UserFlags.from_value(resp.get("public_flags", 0))

        self.voice_state = self.raw.get("voice_state")  # Filled later.

    def __str__(self):
        return f"{self.username}#{self.discriminator}"

    @property
    def mention(self):
        return f"<@{self.id}>"

    def avatar_url(self, *, extension="webp", size=1024):
        if self.avatar:
            return cdn_url("avatars/{user_id}", image_hash=self.avatar, extension=extension, size=size, user_id=self.id)
        else:
            return cdn_url("embed/avatars", image_hash=self.discriminator % 5, extension=extension)

    def set_voice_state(self, voice_state):
        self.voice_state = voice_state
        self.raw["voice_state"] = voice_state

    def get_voice_state(self):
        return self.voice_state


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


class PremiumTypes(TypeBase):
    NONE = 0
    NITRO_CLASSIC = 1
    NITRO = 2
