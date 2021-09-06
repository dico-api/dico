import json
import time
import zlib
import typing
import asyncio
import logging
import aiohttp
from .ratelimit import WSRatelimit
from ..http.async_http import AsyncHTTPRequest
from ..model import gateway
from ..handler import EventHandler


class WebSocketClient:
    ZLIB_SUFFIX = b'\x00\x00\xff\xff'

    def __init__(self,
                 http: AsyncHTTPRequest,
                 ws: aiohttp.ClientWebSocketResponse,
                 base_url: str,
                 intents: typing.Union[gateway.Intents, int],
                 event_handler: EventHandler,
                 try_reconnect: bool):
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
        self.ping = 0.0
        self._ping_start = 0.0
        self.try_reconnect = try_reconnect
        self.ratelimit = WSRatelimit()
        self.buffer = bytearray()
        self.inflator = zlib.decompressobj()
        self.intended_shutdown = False

    def __del__(self):
        if not self._closed:
            self.logger.warning("Please properly close before exiting!")
            self.http.loop.run_until_complete(self.close())

    async def close(self, code: int = 1000):
        if not self._heartbeat_task.cancelled():
            self._heartbeat_task.cancel()
        self.intended_shutdown = True
        if self._closed:
            return
        if not self.ws.closed:
            await self.ws.close(code=code)
        self._closed = True

    async def run(self):
        while True:
            while not self.ws.closed:
                try:
                    msg = await self.ws.receive()
                    resp = await self.receive(msg)
                except Ignore:
                    continue
                except WSClosing as ex:
                    self.logger.warning(f"Websocket is closing with code: {ex.code}")
                    self.intended_shutdown = True
                    if ex.code in (1000, 1001) or self.try_reconnect:
                        self.logger.warning("Trying to reconnect...")
                        await self.reconnect(fresh=True)
                    else:
                        self.logger.error(f"Unexpected websocket disconnection; this client will now be terminated.")
                    break
                if not resp:
                    # self.logger.warning("Empty response detected, ignoring.")
                    # continue

                    # Actually, we should terminate or we might have 500MB+ logger file ¯\_(ツ)_/¯
                    await self.close(1001)
                    raise Exception("Uh oh, it looks like you just encountered some annoying issue. For the safety, this client will be automatically closed.\n"
                                    "If you have the logger set to DEBUG mode, please report this issue with 4~5 previous raw response log to GitHub issue #1 or our support server.\n"
                                    "Sorry for the inconvenience.")
                self.logger.debug(f"Received `{gateway.Opcodes.as_string(resp.op)}` payload"
                                  f"{f' with event name `{resp.t}`' if resp.op == gateway.Opcodes.DISPATCH else ''}.")
                if resp.s:
                    self.seq = resp.s

                proc = await self.process(resp)
                if proc == -1:
                    self.intended_shutdown = True
                    break

            if self._reconnecting or self._fresh_reconnecting:
                self.ws = await self.http.session.ws_connect(self.base_url)
                self._closed = False
                self.intended_shutdown = False
            else:
                if not self.intended_shutdown:
                    self.logger.error("This shutdown is not intended!")
                    if self.ws.closed:
                        self.logger.error("aiohttp websocket is somehow closed, hmm")
                        return
                    continue
                return

    async def request(self, *args, **kwargs):
        async with self.ratelimit.maybe_limited():  # Will raise exception if rate limited, else wait until previous request is done.
            return await self.ws.send_json(*args, **kwargs)

    def to_gateway_response(self, resp) -> gateway.GatewayResponse:
        res = gateway.GatewayResponse(resp)
        if res.s is not None:
            self.seq = res.s
        return res

    async def receive(self, resp: aiohttp.WSMessage):
        # resp = await self.ws.receive()
        self.logger.debug(f"Raw receive {resp.type}: {resp.data}")
        if resp.type == aiohttp.WSMsgType.TEXT:
            return self.to_gateway_response(resp.json())
        elif resp.type == aiohttp.WSMsgType.BINARY:
            msg = resp.data
            self.buffer.extend(msg)
            if len(msg) < 4 or msg[-4:] != self.ZLIB_SUFFIX:
                raise Ignore
            msg = self.inflator.decompress(self.buffer)
            self.buffer = bytearray()
            return self.to_gateway_response(json.loads(msg.decode("UTF-8")))
        elif resp.type == aiohttp.WSMsgType.CONTINUATION:
            raise Ignore
        elif resp.type in (aiohttp.WSMsgType.CLOSE, aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.CLOSING):
            raise WSClosing(resp.data or self.ws.close_code)

    async def process(self, resp):
        if resp.op == gateway.Opcodes.DISPATCH:
            if resp.t == "READY":
                self.session_id = resp.d.get("session_id", self.session_id)
            self.event_handler.client.dispatch("RAW", resp.raw)
            self.event_handler.dispatch_from_raw(resp.t, resp.d)

        elif resp.op == gateway.Opcodes.HELLO:
            self.heartbeat_interval = resp.d["heartbeat_interval"]
            self.ratelimit.reload_heartbeat(self.heartbeat_interval/1000)
            self._heartbeat_task = self.http.loop.create_task(self.run_heartbeat())
            if self._reconnecting:
                await self.resume()
            else:
                await self.identify()
            if self._fresh_reconnecting:
                self._fresh_reconnecting = False

        elif resp.op == gateway.Opcodes.HEARTBEAT_ACK:
            self.last_heartbeat_ack = time.time()
            self.ping = self.last_heartbeat_ack - self._ping_start

        elif resp.op == gateway.Opcodes.INVALID_SESSION:
            self.logger.warning("Failed gateway resume, reconnecting to gateway without resuming.")
            await asyncio.sleep(5)
            await self.reconnect(fresh=True)
            return -1

        elif resp.op == gateway.Opcodes.RECONNECT:
            await self.reconnect()
            return -1

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
        await self.request(data)
        self._reconnecting = False

    async def run_heartbeat(self):
        while not self._closed:
            if not self.last_heartbeat_send <= self.last_heartbeat_ack <= time.time():
                self.logger.warning("Heartbeat timeout, reconnecting...")
                self.http.loop.create_task(self.reconnect())
                break
            data = {"op": gateway.Opcodes.HEARTBEAT, "d": self.seq}
            self._ping_start = time.time()
            await self.ws.send_json(data)  # Don't track rate limit for this.
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
        await self.request(data)

    async def request_guild_members(self, guild_id: str, *, query: str = None, limit: int = None, presences: bool = None, user_ids: typing.List[str] = None, nonce: bool = None):
        d = {"guild_id": guild_id}
        if query is not None:
            d["query"] = query
            d["limit"] = limit
        if presences is not None:
            d["presences"] = presences
        if user_ids is not None:
            d["user_ids"] = user_ids
        if nonce is not None:
            d["nonce"] = nonce
        data = {
            "op": gateway.Opcodes.REQUEST_GUILD_MEMBERS,
            "d": d
        }
        await self.request(data)

    async def update_voice_state(self, guild_id: str, channel_id: typing.Optional[str], self_mute: bool, self_deaf: bool):
        data = {
            "op": gateway.Opcodes.VOICE_STATE_UPDATE,
            "d": {
                "guild_id": guild_id,
                "channel_id": channel_id,
                "self_mute": self_mute,
                "self_deaf": self_deaf
            }
        }
        await self.request(data)

    async def update_presence(self, since: typing.Optional[int], activities: typing.List[dict], status: str, afk: bool):
        data = {
            "op": gateway.Opcodes.PRESENCE_UPDATE,
            "d": {
                "since": since,
                "activities": activities,
                "status": status,
                "afk": afk
            }
        }
        await self.request(data)

    @property
    def closed(self):
        return self._closed

    @classmethod
    async def connect(cls, http, intents, event_handler, try_reconnect, compress):
        resp = await http.request("/gateway/bot", "GET")
        gw = gateway.GetGateway(resp)
        extra = "compress=zlib-stream" if compress else ""
        base_url = gw.url+f"?v=9&encoding=json" + extra
        ws = await http.session.ws_connect(base_url)
        return cls(http, ws, base_url, intents, event_handler, try_reconnect)


class WSClosing(Exception):
    """Internal exception class for controlling WS close event. You should not see this exception in normal situation."""
    def __init__(self, code):
        self.code = code


class Ignore(Exception):
    """Internal exception class for just ignoring the response. Used for ignoring unsupported response."""
