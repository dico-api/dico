import logging
from ..model import gateway


class WebSocketClient:
    BASE_URL = ""

    def __init__(self, http):
        self.ws = None
        self.http = http
        self.logger = logging.getLogger("dico.ws")

    async def connect(self):
        if self.ws:
            raise
        resp = await self.http.request("/gateway/bot", "GET")
        gw = gateway.GetGateway(resp)
        self.BASE_URL = gw.url
        self.ws = self.http.session.ws_connect(self.BASE_URL)
