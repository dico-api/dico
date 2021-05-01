import typing
from .model.snowflake import Snowflake


class CacheContainer:
    def __init__(self, default_expiration_time=None):
        self.default_expiration_time = default_expiration_time
        self.__cache_dict = {"guild_cache": {}}

    def get(self, snowflake_id: typing.Union[str, int, Snowflake], *, ignore_expiration=True):
        for x in self.__cache_dict.values():
            if isinstance(x, dict):
                continue
            res = x.get(snowflake_id, ignore_expiration=ignore_expiration)
            if res:
                return res

    def get_storage(self, storage_type: str):
        if storage_type == "guild_cache":
            return self.__cache_dict["guild_cache"]
        if storage_type not in self.__cache_dict:
            self.__cache_dict[storage_type] = CacheStorage()
        return self.__cache_dict.get(storage_type)

    def get_guild_container(self, guild_id: typing.Union[str, int, Snowflake]):
        guild_caches = self.get_storage("guild_cache")
        guild_id = Snowflake.ensure_snowflake(guild_id)
        if guild_id not in guild_caches:
            guild_caches[guild_id] = GuildCacheContainer(default_expiration_time=self.default_expiration_time)
        return guild_caches[guild_id]

    def add(self, snowflake_id: typing.Union[str, int, Snowflake], obj_type: str, obj, expire_at=None):
        if not expire_at:
            expire_at = self.default_expiration_time

        if obj_type not in self.__cache_dict:
            self.__cache_dict[obj_type] = CacheStorage()
        self.__cache_dict[obj_type].add(Snowflake.ensure_snowflake(snowflake_id), obj, expire_at)

    @property
    def available_cache_types(self):
        return self.__cache_dict.keys()


class GuildCacheContainer(CacheContainer):
    def get_guild_container(self, *args, **kwargs):
        raise NotImplementedError


class CacheStorage:
    def __init__(self):
        self.__cache_dict = {}

    def get(self, snowflake_id: typing.Union[str, int, Snowflake], *, ignore_expiration=True):
        res = self.__cache_dict.get(Snowflake.ensure_snowflake(snowflake_id))
        if res:  # TODO: add expiration time check
            return res["value"]

    def add(self, snowflake_id: typing.Union[str, int, Snowflake], obj, expire_at=None):
        snowflake_id = Snowflake.ensure_snowflake(snowflake_id)
        self.__cache_dict[snowflake_id] = {"value": obj, "expire_at": expire_at}
