import io
import json
import typing
import logging
import asyncio
import aiohttp
from .. import exception
from ..base.http import HTTPRequestBase


class AsyncHTTPRequest(HTTPRequestBase):
    def __init__(self,
                 token: str,
                 loop: asyncio.AbstractEventLoop = None,
                 session: aiohttp.ClientSession = None,
                 default_retry: int = 3):
        self.token = token.lstrip("Bot ")
        self.logger = logging.getLogger("dico.http")
        self.loop = loop or asyncio.get_event_loop()
        self.session = session or aiohttp.ClientSession(loop=self.loop)
        self.default_retry = default_retry
        self._close_on_del = False
        if not session:
            self._close_on_del = True
        self._closed = False

    def __del__(self):
        if not self._closed:
            self.logger.warning("Please properly close before exiting!")
            self.loop.run_until_complete(self.close())

    async def close(self):
        if self._close_on_del:
            await self.session.close()
            self._closed = True

    async def request(self, route: str, meth: str, body: typing.Any = None, is_json: bool = False, *, retry: int = None, **kwargs) -> dict:
        code = 429  # Empty code in case of rate limit fail.
        resp = {}   # Empty resp in case of rate limit fail.
        retry = (retry if retry > 0 else 1) if retry is not None else self.default_retry
        for x in range(retry):
            code, resp = await self._request(route, meth, body, is_json, **kwargs)
            if 200 <= code < 300:
                return resp
            elif code == 403:
                raise exception.Forbidden(route, code, resp)
            elif code == 404:
                raise exception.NotFound(route, code, resp)
            elif code == 429:
                wait_sec = resp["retry_after"]
                self.logger.warning(f"Rate limited, waiting for {wait_sec} second{'s' if wait_sec == 1 else ''}...")
                await asyncio.sleep(wait_sec)
                continue
            elif 500 <= code < 600:
                raise exception.DiscordError(route, code, resp)
            else:
                raise exception.Unknown(route, code, resp)
        raise exception.RateLimited(route, code, resp)

    async def _request(self, route: str, meth: str, body: typing.Any = None, is_json: bool = False, **kwargs) -> typing.Tuple[int, dict]:
        headers = {"Authorization": f"Bot {self.token}"}
        kw = {}
        if meth not in ["GET"] and body:
            if is_json:
                headers["Content-Type"] = "application/json"
                body = json.dumps(body)
            kw["data"] = body
        async with self.session.request(meth, self.BASE_URL+route, headers=headers, **kw) as resp:
            return resp.status, await resp.json()  # if resp.headers.get("Content-Type") == "applications/json" else {"text": await resp.text()}

    def create_message(self,
                       channel_id,
                       content: str,
                       nonce: typing.Union[int, str],
                       tts: bool,
                       embed: dict,
                       allowed_mentions: dict,
                       message_reference: dict):
        if not (content or embed):
            raise
        body = {}
        if content:
            body["content"] = content
        if embed:
            body["embed"] = embed
        if nonce:
            body["nonce"] = nonce
        if tts:
            body["tts"] = tts
        if allowed_mentions:
            body["allowed_mentions"] = allowed_mentions
        if message_reference:
            body["message_reference"] = message_reference
        return self.request(f"/channels/{channel_id}/messages", "POST", body, is_json=True)

    def create_message_with_files(self,
                                  channel_id,
                                  content: str,
                                  files: typing.List[io.FileIO],
                                  nonce: typing.Union[int, str],
                                  tts: bool,
                                  embed: dict,
                                  allowed_mentions: dict,
                                  message_reference: dict):
        if not (content or embed or files):
            raise
        payload_json = {}
        form = aiohttp.FormData()
        if content:
            payload_json["content"] = content
        if embed:
            payload_json["embed"] = embed
        if nonce:
            payload_json["nonce"] = nonce
        if tts:
            payload_json["tts"] = tts
        if allowed_mentions:
            payload_json["allowed_mentions"] = allowed_mentions
        if message_reference:
            payload_json["message_reference"] = message_reference
        form.add_field("payload_json", json.dumps(payload_json), content_type="application/json")
        for x in range(len(files)):
            name = f"file{x if len(files) > 1 else ''}"
            sel = files[x]
            f = sel.read()
            form.add_field(name, f, filename=sel.name, content_type="application/octet-stream")
        return self.request(f"/channels/{channel_id}/messages", "POST", form)

    @classmethod
    def create(cls,
               token: str,
               loop: asyncio.AbstractEventLoop = None,
               session: aiohttp.ClientSession = None,
               default_retry: int = 3):
        return cls(token, loop, session, default_retry)
