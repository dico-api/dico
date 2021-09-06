import copy
import typing

from ..model.snowflake import Snowflake

if typing.TYPE_CHECKING:
    from ..api import APIClient


class CopyableObject:
    def copy(self):
        return copy.copy(self)


class EventBase:
    def __init__(self, client, resp: dict):
        self.raw = resp
        self.client = client
        self._dont_dispatch = False

    @classmethod
    def create(cls, client, resp: dict):
        return cls(client, resp)


class DiscordObjectBase:
    TYPING = typing.Union[int, str, Snowflake, "DiscordObjectBase"]
    RESPONSE = typing.Union["DiscordObjectBase", typing.Awaitable["DiscordObjectBase"]]
    RESPONSE_AS_LIST = typing.Union[typing.List["DiscordObjectBase"], typing.Awaitable[typing.List["DiscordObjectBase"]]]
    _cache_type = None

    def __init__(self, client, resp, **kwargs):
        resp.update(kwargs)
        # self._cache_type = None
        self.raw: dict = resp
        self.id: Snowflake = Snowflake(resp["id"])
        self.client: APIClient = client

    def __int__(self):
        return int(self.id)

    @classmethod
    def create(cls, client, resp, **kwargs):
        ensure_cache_type = kwargs.pop("ensure_cache_type") if "ensure_cache_type" in kwargs else cls._cache_type
        maybe_exist = client.has_cache and client.cache.get(resp["id"], ensure_cache_type)
        if maybe_exist:
            orig = maybe_exist.raw
            for k, v in resp.items():
                if orig.get(k) != v:
                    orig[k] = v
            maybe_exist.__init__(client, orig, **kwargs)
            return maybe_exist
        else:
            ret = cls(client, resp, **kwargs)
            if client.has_cache:
                client.cache.add(ret.id, ret._cache_type, ret)
                if hasattr(ret, "guild_id") and ret.guild_id:
                    client.cache.get_guild_container(ret.guild_id).add(ret.id, ret._cache_type, ret)
            return ret


class AbstractObject(dict):
    RESPONSE = typing.Union["AbstractObject", typing.Awaitable["AbstractObject"]]
    RESPONSE_AS_LIST = typing.Union[typing.List["AbstractObject"], typing.Awaitable[typing.List["AbstractObject"]]]

    def __init__(self, resp):
        super().__init__(**resp)

    def __getattr__(self, item):
        return self.get(item)

    def __setattr__(self, key, value):
        self[key] = value


class FlagBase:
    def __init__(self, *args, **kwargs):
        self.values = {x: getattr(self, x) for x in dir(self) if isinstance(getattr(self, x), int)}
        self.value = 0
        for x in args:
            if x.upper() not in self.values:
                raise AttributeError(f"invalid name: `{x}`")
            self.value |= self.values[x.upper()]
        for k, v in kwargs.items():
            if k.upper() not in self.values:
                raise AttributeError(f"invalid name: `{k}`")
            if v:
                self.value |= self.values[k.upper()]

    def __int__(self):
        return self.value

    def __getattr__(self, item):
        return self.has(item)

    def __iter__(self):
        for k, v in self.values.items():
            if self.has(k):
                yield v

    def has(self, name: str):
        if name.upper() not in self.values:
            raise AttributeError(f"invalid name: `{name}`")
        return (self.value & self.values[name.upper()]) == self.values[name.upper()]

    def __setattr__(self, key, value):
        orig = key
        key = key.upper()
        if orig in ["value", "values"] or key not in self.values.keys():
            return super().__setattr__(orig, value)
        if not isinstance(value, bool):
            raise TypeError(f"only type `bool` is supported.")
        has_value = self.has(key)
        if value and not has_value:
            self.value |= self.values[key]
        elif not value and has_value:
            self.value &= ~self.values[key]

    def add(self, value):
        return self.__setattr__(value, True)

    def remove(self, value):
        return self.__setattr__(value, False)

    @classmethod
    def from_value(cls, value: int):
        ret = cls()
        ret.value = value
        return ret


class TypeBase:
    def __init__(self, value):
        self.values = {getattr(self, x): x for x in dir(self) if isinstance(getattr(self, x), int)}
        self.value = value

        if self.value not in self.values:
            raise AttributeError(f"invalid value: `{value}`")

    def __str__(self):
        return self.values[self.value]

    def __int__(self):
        return self.value

    def __getattr__(self, item):
        return self.is_type(item)

    def is_type(self, name: str):
        values = {y: x for x, y in self.values.items()}
        if name.upper() not in values:
            raise AttributeError(f"invalid name: `{name}`")
        return self.value == values[name.upper()]

    @classmethod
    def to_string(cls, value):
        values = {getattr(cls, x): x for x in dir(cls) if isinstance(getattr(cls, x), int)}
        return values.get(value)
