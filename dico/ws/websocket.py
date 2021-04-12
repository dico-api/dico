import time
import asyncio
import logging
import aiohttp
from ..http.async_http import AsyncHTTPRequest
from ..model import gateway


class WebSocketClient:
    def __init__(self, http: AsyncHTTPRequest, ws: aiohttp.ClientWebSocketResponse, base_url, intents):
        self.ws = ws
        self.http = http
        self.BASE_URL = base_url
        self.logger = logging.getLogger("dico.ws")
        self._closed = False
        self.heartbeat_interval = 0
        self.seq = None
        self.last_heartbeat_ack = 0
        self.last_heartbeat_send = 0
        self._heartbeat_task = None
        self.session_id = None
        self.intents = intents

    def __del__(self):
        if not self._closed:
            self.logger.warning("Please properly close before exiting!")
            self.http.loop.run_until_complete(self.close())

    async def close(self, code: int = 1000):
        if self._closed:
            raise
        self._heartbeat_task.cancel()
        await self.ws.close(code=code)
        self._closed = True

    async def run(self):
        while not self._closed:
            try:
                resp = await self.receive()
            except WSClosing as ex:
                print("closing")
                self.logger.warning(f"Websocket is closing with code: {ex.code}")
                return
            self.logger.debug(f"Received `{gateway.Opcodes.as_string(resp.op)}` payload"
                              f"{f' with event name `{resp.t}`' if resp.op == gateway.Opcodes.DISPATCH else ''}.")
            print(f"Received `{gateway.Opcodes.as_string(resp.op)}` payload")
            if resp.op == gateway.Opcodes.DISPATCH:
                print(f"event name `{resp.t}`")
                print(f"event resp: {resp.d}")
                pass
            elif resp.op == gateway.Opcodes.HELLO:
                self.heartbeat_interval = resp.d["heartbeat_interval"]
                self._heartbeat_task = self.http.loop.create_task(self.run_heartbeat())
                await self.identify()
            elif resp.op == gateway.Opcodes.HEARTBEAT_ACK:
                self.last_heartbeat_ack = time.time()

    async def receive(self):
        resp = await self.ws.receive()
        # print(resp.data)
        # print(resp.type)
        if resp.type == aiohttp.WSMsgType.TEXT:
            res = gateway.GatewayResponse(resp.json())
            self.seq = res.s
            return res
        elif resp.type in (aiohttp.WSMsgType.CLOSE, aiohttp.WSMsgType.CLOSING):  # Somehow this is not mentioned in aiohttp document hmm.
            raise WSClosing(resp.data)

    async def reconnect(self):
        if not self._closed:
            await self.close()

    async def run_heartbeat(self):
        while not self._closed:
            if not self.last_heartbeat_send <= self.last_heartbeat_ack <= time.time():
                # await self.close(4009)
                await self.reconnect()
                break
            data = {"op": gateway.Opcodes.HEARTBEAT, "d": self.seq}
            await self.ws.send_json(data)
            self.last_heartbeat_send = time.time()
            await asyncio.sleep(self.heartbeat_interval/1000)

    async def identify(self):
        data = {
            "op": gateway.Opcodes.IDENTIFY,
            "d": {
                "token": self.http.token,
                "intents": self.intents,
                "properties": {
                    "$os": "linux",
                    "$browser": "dico",
                    "$device": "dico"
                }
            }
        }
        await self.ws.send_json(data)

    @classmethod
    async def connect(cls, http, intents):
        resp = await http.request("/gateway/bot", "GET")
        gw = gateway.GetGateway(resp)
        base_url = gw.url+f"?v=8&encoding=json"
        ws = await http.session.ws_connect(base_url)
        return cls(http, ws, base_url, intents)


class WSClosing(Exception):
    """Internal exception class for controlling WS close event. You should not see this exception in normal situation."""
    def __init__(self, code):
        self.code = code
