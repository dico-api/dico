from ..model.snowflake import Snowflake


class EventBase:
    def __init__(self, client, resp: dict):
        self.raw = resp
        self.client = client

    @classmethod
    def create(cls, client, resp: dict):
        return cls(client, resp)


class DiscordObjectBase:
    def __init__(self, client, resp, **kwargs):
        resp.update(kwargs)
        self._cache_type = None
        self.raw = resp
        self.id = Snowflake(resp["id"])
        self.client = client

    def __int__(self):
        return int(self.id)

    @classmethod
    def create(cls, client, resp, **kwargs):
        maybe_exist = client.cache.get(resp["id"])
        if maybe_exist:
            orig = maybe_exist.raw
            for k, v in resp.items():
                if orig.get(k) != v:
                    orig[k] = v
            maybe_exist.__init__(client, orig, **kwargs)
            return maybe_exist
        else:
            ret = cls(client, resp, **kwargs)
            client.cache.add(ret.id, ret._cache_type, ret)
            if hasattr(ret, "guild_id") and ret.guild_id:
                client.cache.get_guild_container(ret.guild_id).add(ret.id, ret._cache_type, ret)
            return ret


class FlagBase:
    def __init__(self, *args, **kwargs):
        self.values = {x: getattr(self, x) for x in dir(self) if isinstance(getattr(self, x), int)}
        self.enabled = []
        self.__setattr__ = self.__setattr
        for x in args:
            if x.upper() not in self.values.keys():
                raise
            self.enabled.append(x.upper())
        for k, v in kwargs.items():
            if k.upper() not in self.values:
                raise AttributeError(f"invalid name: `{k}`")
            if v:
                self.enabled.append(k.upper())

    def __int__(self):
        return sum([self.values[x] for x in self.enabled])

    def __setattr(self, key, value):
        if not isinstance(value, bool):
            raise TypeError(f"only type `bool` is supported.")
        o_key = key
        key = key.upper()
        if key not in self.values.keys():
            raise AttributeError(f"invalid name: `{o_key}`")
        if not value and key in self.enabled:
            self.enabled.remove(key)
        elif value and key not in self.enabled:
            self.enabled.append(key)

    def add(self, value):
        o_value = value
        value = value.upper()
        if value not in self.values.keys():
            raise AttributeError(f"invalid name: `{o_value}`")
        if value not in self.enabled:
            self.enabled.append(value)

    def remove(self, value):
        o_value = value
        value = value.upper()
        if value not in self.values.keys():
            raise AttributeError(f"invalid name: `{o_value}`")
        if value in self.enabled:
            self.enabled.remove(value)
