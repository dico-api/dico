import typing
from .model.snowflake import Snowflake


class ClientCacheContainer:
    def __init__(self, default_expiration_time=None):
        self.default_expiration_time = default_expiration_time
        self.__cache_dict = {}

    def get(self, snowflake_id: typing.Union[str, int, Snowflake], *, ignore_expiration=True):
        for x in self.__cache_dict.values():
            res = x.get(snowflake_id, ignore_expiration)
            if res:
                return res

    def get_storage(self, storage_type: str):
        if storage_type not in self.__cache_dict:
            self.__cache_dict[storage_type] = CacheStorage()
        return self.__cache_dict.get(storage_type)

    def add(self, snowflake_id: typing.Union[str, int, Snowflake], obj_type: str, obj, expire_at=None):
        if not expire_at:
            expire_at = self.default_expiration_time

        if obj_type not in self.__cache_dict:
            self.__cache_dict[obj_type] = CacheStorage()
        self.__cache_dict[obj_type].add(snowflake_id, obj, expire_at)

    @property
    def available_cache_types(self):
        return self.__cache_dict.keys()


class CacheStorage:
    def __init__(self):
        self.__cache_dict = {}

    def get(self, snowflake_id: typing.Union[str, int, Snowflake], *, ignore_expiration=True):
        res = self.__cache_dict.get(Snowflake.ensure_snowflake(snowflake_id))
        if res and (not ignore_expiration or res["expire_at"]):  # TODO: add expiration time check
            return res["value"]

    def add(self, snowflake_id: typing.Union[str, int, Snowflake], obj, expire_at=None):
        snowflake_id = Snowflake.ensure_snowflake(snowflake_id)
        self.__cache_dict[snowflake_id] = {"value": obj, "expire_at": expire_at}
