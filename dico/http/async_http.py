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
            elif code == 400:
                raise exception.BadRequest(route, code, resp)
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
        if meth not in ["GET"] and body is not None:
            if is_json:
                headers["Content-Type"] = "application/json"
                body = json.dumps(body)
            kwargs["data"] = body
        async with self.session.request(meth, self.BASE_URL+route, headers=headers, **kwargs) as resp:
            self.logger.debug(f"{route}: {meth} request - {resp.status}")
            return resp.status, await resp.json() if resp.status != 204 else None  # if resp.headers.get("Content-Type") == "applications/json" else {"text": await resp.text()}

    def create_message_with_files(self,
                                  channel_id,
                                  content: str = None,
                                  files: typing.List[io.FileIO] = None,
                                  nonce: typing.Union[int, str] = None,
                                  tts: bool = None,
                                  embed: dict = None,
                                  allowed_mentions: dict = None,
                                  message_reference: dict = None,
                                  components: typing.List[dict] = None):
        if not (content or embed or files):
            raise ValueError("either content or embed or files must be passed.")
        payload_json = {}
        form = aiohttp.FormData()
        if content:
            payload_json["content"] = content
        if embed:
            payload_json["embed"] = embed
        if nonce:
            payload_json["nonce"] = nonce
        if tts is not None:
            payload_json["tts"] = tts
        if allowed_mentions:
            payload_json["allowed_mentions"] = allowed_mentions
        if message_reference:
            payload_json["message_reference"] = message_reference
        if components:
            payload_json["components"] = components
        form.add_field("payload_json", json.dumps(payload_json), content_type="application/json")
        for x in range(len(files)):
            name = f"file{x if len(files) > 1 else ''}"
            sel = files[x]
            f = sel.read()
            form.add_field(name, f, filename=sel.name, content_type="application/octet-stream")
        return self.request(f"/channels/{channel_id}/messages", "POST", form)

    def edit_message_with_files(self,
                                channel_id,
                                message_id,
                                content: str = None,
                                embed: dict = None,
                                flags: int = None,
                                files: typing.List[io.FileIO] = None,
                                allowed_mentions: dict = None,
                                attachments: typing.List[dict] = None,
                                components: typing.List[dict] = None):
        payload_json = {}
        form = aiohttp.FormData()
        if content is not None:
            payload_json["content"] = content
        if embed is not None:
            payload_json["embed"] = embed
        if flags is not None:
            payload_json["flags"] = flags
        if allowed_mentions is not None:
            payload_json["allowed_mentions"] = allowed_mentions
        if attachments is not None:
            payload_json["attachments"] = attachments
        if components is not None:
            payload_json["components"] = components
        form.add_field("payload_json", json.dumps(payload_json), content_type="application/json")
        for x in range(len(files)):
            name = f"file{x if len(files) > 1 else ''}"
            sel = files[x]
            f = sel.read()
            form.add_field(name, f, filename=sel.name, content_type="application/octet-stream")
        return self.request(f"/channels/{channel_id}/messages/{message_id}", "PATCH", form)

    def execute_webhook_with_files(self,
                                   webhook_id,
                                   webhook_token,
                                   wait: bool = None,
                                   thread_id=None,
                                   content: str = None,
                                   username: str = None,
                                   avatar_url: str = None,
                                   tts: bool = False,
                                   files: typing.List[io.FileIO] = None,
                                   embeds: typing.List[dict] = None,
                                   allowed_mentions: dict = None,
                                   flags: int = None):
        if not (content or embeds or files):
            raise ValueError("either content or embeds or files must be passed.")
        payload_json = {}
        form = aiohttp.FormData()
        if content is not None:
            payload_json["content"] = content
        if username is not None:
            payload_json["username"] = username
        if avatar_url is not None:
            payload_json["avatar_url"] = avatar_url
        if tts is not None:
            payload_json["tts"] = tts
        if embeds is not None:
            payload_json["embeds"] = embeds
        if allowed_mentions is not None:
            payload_json["allowed_mentions"] = allowed_mentions
        if flags is not None:
            payload_json["flags"] = flags
        params = {}
        if wait is not None:
            params["wait"] = wait
        if thread_id is not None:
            params["thread_id"] = thread_id
        form.add_field("payload_json", json.dumps(payload_json), content_type="application/json")
        for x in range(len(files)):
            name = f"file{x if len(files) > 1 else ''}"
            sel = files[x]
            f = sel.read()
            form.add_field(name, f, filename=sel.name, content_type="application/octet-stream")
        return self.request(f"/webhooks/{webhook_id}/{webhook_token}", "POST", form, params=params)

    def edit_webhook_message(self,
                             webhook_id,
                             webhook_token,
                             message_id,
                             content: str = None,
                             embeds: typing.List[dict] = None,
                             files: typing.List[io.FileIO] = None,
                             allowed_mentions: dict = None,
                             attachments: typing.List[dict] = None):
        payload_json = {}
        form = aiohttp.FormData()
        if content is not None:
            payload_json["content"] = content
        if embeds is not None:
            payload_json["embeds"] = embeds
        if allowed_mentions is not None:
            payload_json["allowed_mentions"] = allowed_mentions
        if attachments is not None:
            payload_json["attachments"] = attachments
        form.add_field("payload_json", json.dumps(payload_json), content_type="application/json")
        if files:
            for x in range(len(files)):
                name = f"file{x if len(files) > 1 else ''}"
                sel = files[x]
                f = sel.read()
                form.add_field(name, f, filename=sel.name, content_type="application/octet-stream")
        return self.request(f"/webhooks/{webhook_id}/{webhook_token}/messages/{message_id}", "PATCH", form)

    async def download(self, url):
        async with self.session.get(url) as resp:
            if resp.status == 200:
                return await resp.read()
            else:
                self.logger.error(f"Download failed with {resp.status}: {url}")
                raise exception.HTTPError(url, resp.status, await resp.read())

    @classmethod
    def create(cls,
               token: str,
               loop: asyncio.AbstractEventLoop = None,
               session: aiohttp.ClientSession = None,
               default_retry: int = 3):
        return cls(token, loop, session, default_retry)
