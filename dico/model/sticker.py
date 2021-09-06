import typing
from .snowflake import Snowflake
from .user import User
from ..base.model import DiscordObjectBase, TypeBase
from ..utils import cdn_url


class Sticker(DiscordObjectBase):
    TYPING = typing.Union[int, str, Snowflake, "Sticker"]
    RESPONSE = typing.Union["Sticker", typing.Awaitable["Sticker"]]
    RESPONSE_AS_LIST = typing.Union[typing.List["Sticker"], typing.Awaitable[typing.List["Sticker"]]]
    _cache_type = "sticker"

    def __init__(self, client, resp):
        super().__init__(client, resp)
        self.pack_id: typing.Optional[Snowflake] = Snowflake.optional(resp.get("pack_id"))
        self.name: str = resp["name"]
        self.description: typing.Optional[str] = resp["description"]
        self.tags: str = resp["tags"]
        self.type: StickerTypes = StickerTypes(resp["type"])
        self.format_type: StickerFormatTypes = StickerFormatTypes(resp["format_type"])
        self.available: typing.Optional[bool] = resp.get("available")
        self.guild_id: typing.Optional[Snowflake] = Snowflake.optional(resp.get("guild_id"))
        self.__user = resp.get("user")
        self.user: typing.Optional[User] = User.create(client, self.__user) if self.__user else self.__user
        self.sort_value: typing.Optional[int] = resp.get("sort_value")

    def __str__(self):
        return self.name

    @property
    def guild(self):
        if self.client.has_cache:
            return self.client.get(self.guild_id, "guild")  # noqa

    @property
    def pack(self):
        if self.client.has_cache:
            return self.client.get(self.pack_id, "sticker_pack")  # noqa


class StickerTypes(TypeBase):
    STANDARD = 1
    GUILD = 2


class StickerFormatTypes(TypeBase):
    PNG = 1
    APNG = 2
    LOTTIE = 3


class StickerItem:
    def __init__(self, resp):
        self.id: Snowflake = Snowflake(resp["id"])
        self.name: str = resp["name"]
        self.format_type: StickerFormatTypes = StickerFormatTypes(resp["format_type"])

    def __str__(self):
        return self.name

    def __int__(self):
        return int(self.id)


class StickerPack(DiscordObjectBase):
    TYPING = typing.Union[int, str, Snowflake, "StickerPack"]
    RESPONSE = typing.Union["StickerPack", typing.Awaitable["StickerPack"]]
    RESPONSE_AS_LIST = typing.Union[typing.List["StickerPack"], typing.Awaitable[typing.List["StickerPack"]]]
    _cache_type = "sticker_pack"

    def __init__(self, client, resp):
        super().__init__(client, resp)
        self.stickers: typing.List[Sticker] = [Sticker.create(client, x) for x in resp["stickers"]]
        self.name: str = resp["name"]
        self.sku_id: Snowflake = Snowflake(resp["sku_id"])
        self.cover_sticker_id: typing.Optional[Snowflake] = Snowflake.optional(resp.get("cover_sticker_id"))
        self.description: str = resp["description"]
        self.banner_asset_id: Snowflake = Snowflake(resp["banner_asset_id"])

    def __str__(self):
        return self.name

    def banner_url(self, *, extension="webp", size=1024):
        return cdn_url("app-assets/710982414301790216/store", image_hash=self.banner_asset_id, extension=extension, size=size)
