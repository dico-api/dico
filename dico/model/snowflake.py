import datetime


class Snowflake:
    def __init__(self, snowflake):
        self.__snowflake = int(snowflake)

    @property
    def timestamp(self):
        return datetime.datetime.fromtimestamp(((self.__snowflake >> 22) + 1420070400000)/1000)

    @property
    def increment(self):
        return self.__snowflake & 0xFFF

    @property
    def wid(self):
        return (self.__snowflake & 0x3E0000) >> 17

    @property
    def pid(self):
        return (self.__snowflake & 0x1F000) >> 12

    @property
    def id(self):
        return self.__snowflake

    def __str__(self):
        return str(self.__snowflake)

    def __int__(self):
        return self.__snowflake

    def __eq__(self, other):
        return self.__snowflake == int(other)

    def __ne__(self, other):
        return self.__snowflake != int(other)

    def __lt__(self, other):
        return self.__snowflake < int(other)

    def __le__(self, other):
        return self.__snowflake <= int(other)

    def __gt__(self, other):
        return self.__snowflake > int(other)

    def __ge__(self, other):
        return self.__snowflake >= int(other)

    def __hash__(self):
        return hash(self.__snowflake)

    @classmethod
    def optional(cls, snowflake):
        return cls(snowflake) if snowflake else snowflake

    @classmethod
    def ensure_snowflake(cls, target):
        return target if isinstance(target, cls) else cls.optional(target)
