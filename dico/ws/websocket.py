import time
import typing
import asyncio
import logging
import aiohttp
from ..http.async_http import AsyncHTTPRequest
from ..model import gateway
from ..handler import EventHandler


class WebSocketClient:
    def __init__(self,
                 http: AsyncHTTPRequest,
                 ws: aiohttp.ClientWebSocketResponse,
                 base_url: str,
                 intents: typing.Union[gateway.Intents, int],
                 event_handler: EventHandler):
        self.ws = ws
        self.http = http
        self.base_url = base_url
        self.event_handler = event_handler
        self.logger = logging.getLogger("dico.ws")
        self._closed = False
        self._reconnecting = False
        self._fresh_reconnecting = False
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
        if not self._heartbeat_task.cancelled():
            self._heartbeat_task.cancel()
        if self._closed:
            return
        await self.ws.close(code=code)
        self._closed = True

    async def run(self):
        while True:
            while not self._closed:
                try:
                    resp = await self.receive()
                except WSClosing as ex:
                    self.logger.warning(f"Websocket is closing with code: {ex.code}")
                    break
                self.logger.debug(f"Received `{gateway.Opcodes.as_string(resp.op)}` payload"
                                  f"{f' with event name `{resp.t}`' if resp.op == gateway.Opcodes.DISPATCH else ''}.")
                if resp.s:
                    self.seq = resp.s

                if resp.op == gateway.Opcodes.DISPATCH:
                    if resp.t == "READY":
                        self.session_id = resp.d.get("session_id", self.session_id)
                    self.event_handler.dispatch_from_raw(resp.t, resp.d)

                elif resp.op == gateway.Opcodes.HELLO:
                    self.heartbeat_interval = resp.d["heartbeat_interval"]
                    self._heartbeat_task = self.http.loop.create_task(self.run_heartbeat())
                    if self._reconnecting:
                        await self.resume()
                    else:
                        await self.identify()
                    if self._fresh_reconnecting:
                        self._fresh_reconnecting = False

                elif resp.op == gateway.Opcodes.HEARTBEAT_ACK:
                    self.last_heartbeat_ack = time.time()

                elif resp.op == gateway.Opcodes.INVALID_SESSION:
                    self.logger.warning("Failed gateway resume, reconnecting to gateway without resuming.")
                    await asyncio.sleep(5)
                    await self.reconnect(fresh=True)
                    break

                elif resp.op == gateway.Opcodes.RECONNECT:
                    await self.reconnect()
                    break

            if self._reconnecting or self._fresh_reconnecting:
                self.ws = await self.http.session.ws_connect(self.base_url)
                self._closed = False
            else:
                return

    async def receive(self):
        resp = await self.ws.receive()
        if resp.type == aiohttp.WSMsgType.TEXT:
            res = gateway.GatewayResponse(resp.json())
            self.seq = res.s
            return res
        elif resp.type in (aiohttp.WSMsgType.CLOSE, aiohttp.WSMsgType.CLOSING, aiohttp.WSMsgType.CLOSED):  # Somehow this is not mentioned in aiohttp document hmm.
            raise WSClosing(resp.data)

    async def reconnect(self, fresh: bool = False):
        if self._reconnecting or self._fresh_reconnecting:
            self.logger.warning("Reconnection is already running, but another reconnection is requested. This request is ignored.")
            return
        self._reconnecting = not fresh
        self._fresh_reconnecting = fresh
        self.logger.info("Reconnecting to Websocket...")
        if not self._closed:
            await self.close(4000)

    async def resume(self):
        data = {
            "op": gateway.Opcodes.RESUME,
            "d": {
                "token": self.http.token,
                "session_id": self.session_id,
                "seq": self.seq
            }
        }
        await self.ws.send_json(data)
        self._reconnecting = False

    async def run_heartbeat(self):
        while not self._closed:
            if not self.last_heartbeat_send <= self.last_heartbeat_ack <= time.time():
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
                "intents": int(self.intents),
                "properties": {
                    "$os": "linux",
                    "$browser": "dico",
                    "$device": "dico"
                }
            }
        }
        await self.ws.send_json(data)

    @classmethod
    async def connect(cls, http, intents, event_handler):
        resp = await http.request("/gateway/bot", "GET")
        gw = gateway.GetGateway(resp)
        base_url = gw.url+f"?v=8&encoding=json"
        ws = await http.session.ws_connect(base_url)
        return cls(http, ws, base_url, intents, event_handler)


class WSClosing(Exception):
    """Internal exception class for controlling WS close event. You should not see this exception in normal situation."""
    def __init__(self, code):
        self.code = code
