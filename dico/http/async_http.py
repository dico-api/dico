import typing
import logging
import asyncio
import aiohttp
from .. import exception
from ..base.http import HTTPRequestBase


class AsyncHTTPRequest(HTTPRequestBase):
    BASE_URL = "https://discord.com/api/v8"

    def __init__(self, token: str, loop: asyncio.AbstractEventLoop = None, session: aiohttp.ClientSession = None):
        self.token = token.lstrip("Bot ")
        self.logger = logging.getLogger("dico.http")
        self.loop = loop or asyncio.get_event_loop()
        self.session = session or aiohttp.ClientSession(loop=self.loop)
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

    async def request(self, route: str, meth: str, body: dict = None, *, retry: int = 3, **kwargs) -> dict:
        code = 429  # Empty code in case of rate limit fail.
        resp = {}   # Empty resp in case of rate limit fail.
        for x in range(retry):
            code, resp = await self._request(route, meth, body, **kwargs)
            if code == 200:
                return resp
            elif code == 429:
                wait_sec = resp["retry_after"]
                self.logger.warning(f"Rate limited, waiting for {wait_sec} second{'s' if wait_sec ==1 else ''}...")
                await asyncio.sleep(wait_sec)
                continue
            elif 500 <= code < 600:
                raise exception.DiscordError(route, code, resp)
            else:
                raise exception.Unknown(route, code, resp)
        raise exception.RateLimited(route, code, resp)

    async def _request(self, route: str, meth: str, body: str = None, **kwargs) -> typing.Tuple[int, dict]:
        headers = {"Authorization": f"Bot {self.token}"}
        kw = {}
        if meth not in ["GET"]:
            kw["body"] = body
        async with self.session.request(meth, self.BASE_URL+route, headers=headers, **kw) as resp:
            return resp.status, await resp.json()  # if resp.headers.get("Content-Type") == "applications/json" else {"text": await resp.text()}
