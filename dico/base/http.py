import typing
from abc import ABC, abstractmethod


class HTTPRequestBase(ABC):

    @abstractmethod
    def request(self, route: str, meth: str, body: dict = None, *, retry: int = 3, **kwargs):
        """
        This function should wrap :meth:`._request` with rate limit handling.
        :return:
        """
        pass

    @abstractmethod
    def _request(self, route: str, meth: str, body: dict = None, **kwargs) -> typing.Tuple[int, dict]:
        """
        HTTP Requesting part.
        :return: Tuple[int, dict]
        """
        pass
