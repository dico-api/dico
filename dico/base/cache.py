from abc import ABC, abstractmethod


class CacheContainerBase(ABC):

    @abstractmethod
    def get(self, snowflake_id: int, safe=True):
        pass

    @abstractmethod
    def add(self, snowflake_id: int, obj_type, obj, expire_at=None):
        pass
