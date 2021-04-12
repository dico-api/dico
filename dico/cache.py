from .base.cache import CacheContainerBase


class ClientCacheContainer(CacheContainerBase):
    def __init__(self, default_expiration_time=None):
        self.default_expiration_time = default_expiration_time
        self.__cache_dict = {}

    def get(self, snowflake_id: int, safe=True):
        pass

    def add(self, snowflake_id: int, obj_type: str, obj, expire_at=None):
        if not expire_at:
            expire_at = self.default_expiration_time

        if obj_type not in self.__cache_dict:
            self.__cache_dict[obj_type] = {}
        self.__cache_dict[obj_type].add(snowflake_id, obj, expire_at)


class CacheStorage:
    def __init__(self):
        pass

    def get(self, snowflake_id: int, safe=True):
        pass

    def add(self, snowflake_id: int, obj, expire_at=None):
        pass
