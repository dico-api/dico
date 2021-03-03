from abc import ABC, abstractmethod


class HTTPRequestBase(ABC):

    @abstractmethod
    def request(self):
        pass
