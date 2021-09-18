import typing
from .model.snowflake import Snowflake


class CacheContainer:
    def __init__(self, default_expiration_time=None, **max_sizes):
        self.default_expiration_time = default_expiration_time
        self.__cache_dict: typing.Dict[str, typing.Union[dict, CacheStorage]] = {"guild_cache": {}}
        self.max_sizes = max_sizes

    def get(self, snowflake_id: typing.Union[str, int, Snowflake], storage_type: str = None, *, ignore_expiration=True):
        if storage_type:
            return self.get_storage(storage_type).get(snowflake_id, ignore_expiration=ignore_expiration)
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
            self.__cache_dict[storage_type] = CacheStorage(max_size=self.max_sizes.get(storage_type, 0), root_remove=self.remove, cache_type=storage_type)
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
            self.__cache_dict[obj_type] = CacheStorage(max_size=self.max_sizes.get(obj_type, 0), root_remove=self.remove, cache_type=obj_type)
        self.__cache_dict[obj_type].add(Snowflake.ensure_snowflake(snowflake_id), obj, expire_at)

    def remove(self, snowflake_id: typing.Union[str, int, Snowflake], obj_type: str):
        if obj_type in self.__cache_dict:
            self.__cache_dict[obj_type].remove(snowflake_id)
        if "guild_cache" in self.__cache_dict:
            for x in self.__cache_dict["guild_cache"].values():
                x.remove(snowflake_id, obj_type)

    def get_size(self, cache_type: str):
        storage = self.get_storage(cache_type)
        return storage.size

    @property
    def available_cache_types(self):
        return self.__cache_dict.keys()

    @property
    def size(self):
        ret = 0
        for k, v in self.__cache_dict.items():
            if k == "guild_cache":
                for b in v.values():
                    ret += b.size
                continue
            ret += v.size
        return ret


class GuildCacheContainer(CacheContainer):
    def get_guild_container(self, *args, **kwargs):
        raise NotImplementedError


class CacheStorage:
    def __init__(self, max_size: int = 0, root_remove=None, cache_type=None):
        self.__cache_dict = {}
        self.max_size = max_size
        self._root_remove = root_remove
        self.cache_type = cache_type

    def __iter__(self):
        for x in self.__cache_dict.values():
            yield x

    def get(self, snowflake_id: typing.Union[str, int, Snowflake], *, ignore_expiration=True):
        res = self.__cache_dict.get(Snowflake.ensure_snowflake(snowflake_id))
        if res:  # TODO: add expiration time check
            return res["value"]

    def add(self, snowflake_id: typing.Union[str, int, Snowflake], obj, expire_at=None):
        snowflake_id = Snowflake.ensure_snowflake(snowflake_id)
        self.__cache_dict[snowflake_id] = {"value": obj, "expire_at": expire_at}
        if 0 < self.max_size < self.size:
            while self.size > self.max_size:
                key = (*self.__cache_dict.keys(),)[0]
                self._root_remove(key, self.cache_type)
                # del self.__cache_dict[key]

    def remove(self, snowflake_id: typing.Union[str, int, Snowflake]):
        snowflake_id = Snowflake.ensure_snowflake(snowflake_id)
        if snowflake_id in self.__cache_dict:
            self.__cache_dict.pop(snowflake_id)

    @property
    def size(self):
        return len(self.__cache_dict)
