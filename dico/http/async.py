import typing
import asyncio
import aiohttp
from .. import exception
from ..base.http import HTTPRequestBase


class AsyncHTTPRequest(HTTPRequestBase):
    BASE_URL = "https://discord.com/api/v8"

    def __init__(self, token: str, loop: asyncio.AbstractEventLoop = None, session: aiohttp.ClientSession = None):
        self.token = token.lstrip("Bot ")
        self.loop = loop or asyncio.get_event_loop()
        self.session = session or aiohttp.ClientSession(loop=self.loop)
        self._close_on_del = False
        if not session:
            self._close_on_del = True

    async def close(self):
        if self._close_on_del:
            await self.session.close()

    async def request(self, route: str, meth: str, body: dict = None, *, retry: int = 3, **kwargs):
        code = 429  # Empty code in case of rate limit fail.
        resp = {}   # Empty resp in case of rate limit fail.
        for x in range(retry):
            code, resp = await self._request(route, meth, body, **kwargs)
            if code == 200:
                return resp
            elif code == 429:
                continue
            elif 500 <= code < 600:
                raise exception.DiscordError(route, code, resp)
            else:
                raise exception.Unknown(route, code, resp)
        raise exception.RateLimited(route, code, resp)

    async def _request(self, route: str, meth: str, body: dict = None, **kwargs) -> typing.Tuple[int, dict]:
        headers = {"Authorization": f"Bot {self.token}"}
        async with self.session.request(meth, self.BASE_URL+route, headers=headers) as resp:
            return resp.status, await resp.json() if resp.headers.get("Content-Type") == "applications/json" else await resp.text()
