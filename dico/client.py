from .http.async_http import AsyncHTTPRequest
from .ws.websocket import WebSocketClient
from .cache import ClientCacheContainer


class Client:
    def __init__(self, token: str):
        self.token = token
        self.http = AsyncHTTPRequest(self.token)
        self.cache = ClientCacheContainer()
        self.ws = WebSocketClient(self.http, self.cache)
