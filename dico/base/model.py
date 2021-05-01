from ..model.snowflake import Snowflake


class EventBase:
    def __init__(self, client, resp: dict):
        self.raw = resp

    @classmethod
    def create(cls, client, resp: dict):
        return cls(client, resp)


class DiscordObjectBase:
    def __init__(self, client, resp):
        self.raw = resp
        self.id = Snowflake(resp["id"])
        self.client = client

    def __int__(self):
        return int(self.id)


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
