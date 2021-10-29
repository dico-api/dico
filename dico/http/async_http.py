import io
import json
import typing
import logging
import asyncio
import aiohttp
from .ratelimit import RatelimitHandler
from .. import exception, __version__
from ..base.http import HTTPRequestBase, EmptyObject, _R


ASYNC_RESPONSE = typing.Awaitable[_R]


class AsyncHTTPRequest(HTTPRequestBase):
    """
    Async HTTP request client.

    .. warning::
        This module isn't intended to be directly used. It is recommended to request via APIClient.

    :param token: Application token to use.
    :param loop: AsyncIO loop instance to use. Default ``asyncio.get_event_loop()``.
    :param session: Optional ClientSession to use.
    :param default_retry: Maximum retry count. Default 3.

    :ivar token: Application token of the client.
    :ivar logger: Logger instance of the client.
    :ivar session: ClientSession of the client.
    :ivar default_retry: Maximum retry count of the client.
    :ivar ratelimits: :class:`.ratelimit.RatelimitHandler` of the client.
    """
    def __init__(self,
                 token: str,
                 loop: typing.Optional[asyncio.AbstractEventLoop] = None,
                 session: typing.Optional[aiohttp.ClientSession] = None,
                 default_retry: int = 3):
        self.token: str = token.lstrip("Bot ")
        self.logger: logging.Logger = logging.getLogger("dico.http")
        self.loop: asyncio.AbstractEventLoop = loop or asyncio.get_event_loop()
        self.session: aiohttp.ClientSession = session or aiohttp.ClientSession(loop=self.loop)
        self.default_retry: int = default_retry
        self._close_on_del: bool = False
        if not session:
            self._close_on_del = True
        self._closed: bool = False
        self.ratelimits: RatelimitHandler = RatelimitHandler()

    def __del__(self):
        if not self._closed:
            self.logger.warning("Please properly close before exiting!")
            self.loop.run_until_complete(self.close())

    async def close(self):
        """Closes session and marks this client as closed."""
        if self._close_on_del:
            await self.session.close()
        self._closed = True

    async def request(self,
                      route: str,
                      meth: str,
                      body: typing.Optional[typing.Any] = None,
                      *,
                      is_json: bool = False,
                      reason_header: typing.Optional[str] = None,
                      retry: int = None,
                      **kwargs) -> _R:
        """
        Sends request to Discord API.

        :param route: Route to request.
        :param meth: Method to use.
        :param body: Body of the request.
        :param is_json: Whether the body is JSON.
        :param reason_header: Reason to show in audit log.
        :param retry: Retry count in rate limited situation.
        :param kwargs: Extra options to add.
        :return: Response.
        :raises BadRequest: This request is incorrect.
        :raises Forbidden: You do not have permission for this action.
        :raises DiscordError: Something is wrong with Discord right now.
        :raises Unknown: We are unable to handle this error, sorry.
        :raises RateLimited: We are rate limited, please try again later.
        """
        code = 429  # Empty code in case of rate limit fail.
        resp = {}   # Empty resp in case of rate limit fail.
        retry = (retry if retry > 0 else 1) if retry is not None else self.default_retry
        for x in range(retry):
            code, resp = await self._request(route, meth, body, is_json, reason_header, **kwargs)
            if 200 <= code < 300:
                return resp
            elif code == 400:
                raise exception.BadRequest(route, code, resp)
            elif code == 403:
                raise exception.Forbidden(route, code, resp)
            elif code == 404:
                raise exception.NotFound(route, code, resp)
            elif code == 429:
                continue
            elif 500 <= code < 600:
                raise exception.DiscordError(route, code, resp)
            else:
                raise exception.Unknown(route, code, resp)
        raise exception.RateLimited(route, code, resp)

    async def _request(self, route: str, meth: str, body: typing.Optional[typing.Any] = None, is_json: bool = False, reason_header: str = None, **kwargs) \
            -> typing.Tuple[int, typing.Union[dict, typing.Any]]:
        await self.ratelimits.maybe_global()
        locker = self.ratelimits.get_locker(meth, route)
        async with locker["lock"]:
            if "remaining" in locker and "reset_at" in locker and locker["remaining"] == 0 and self.ratelimits.utc < locker["reset_at"]:
                wait_time = (locker["reset_at"] - self.ratelimits.utc).total_seconds()
                self.logger.warning(f"No more remaining request count, waiting for {wait_time} seconds...")
                await asyncio.sleep(wait_time)
            headers = {"Authorization": f"Bot {self.token}", "User-Agent": f"DiscordBot (https://github.com/dico-api/dico, {__version__})"}
            if meth not in ["GET"] and body is not None:
                if is_json:
                    headers["Content-Type"] = "application/json"
                    body = json.dumps(body)
                kwargs["data"] = body
            if reason_header is not None:
                headers["X-Audit-Log-Reason"] = reason_header
            async with self.session.request(meth, self.BASE_URL + route, headers=headers, **kwargs) as resp:
                self.logger.debug(f"{route}: {meth} request - {resp.status}")
                bucket = resp.headers.get("X-RateLimit-Bucket")
                reset_after = resp.headers.get("X-RateLimit-Reset-After")
                reset_at = resp.headers.get("X-RateLimit-Reset")
                remaining = resp.headers.get("X-RateLimit-Remaining")
                self.ratelimits.set_bucket(meth, route, bucket, reset_after, reset_at, remaining)
                maybe_json = await (resp.json() if resp.headers.get("Content-Type") == "application/json" else resp.text()) if resp.status != 204 else None
                if isinstance(maybe_json, dict) and resp.status == 429:
                    wait_sec = float(maybe_json["retry_after"])
                    if maybe_json["global"]:
                        async with self.ratelimits.global_locker:
                            self.logger.warning(f"Rate limited globally, waiting for {wait_sec} second{'s' if wait_sec == 1 else ''}...")
                            await asyncio.sleep(wait_sec)
                    else:
                        self.logger.warning(f"Rate limited, waiting for {wait_sec} second{'s' if wait_sec == 1 else ''}...")
                        await asyncio.sleep(wait_sec)
                return resp.status, maybe_json  # if resp.headers.get("Content-Type") == "applications/json" else {"text": await resp.text()}

    def create_message_with_files(self,
                                  channel_id,
                                  content: str = None,
                                  files: typing.List[io.FileIO] = None,
                                  nonce: typing.Union[int, str] = None,
                                  tts: bool = None,
                                  embeds: typing.List[dict] = None,
                                  allowed_mentions: dict = None,
                                  message_reference: dict = None,
                                  components: typing.List[dict] = None,
                                  sticker_ids: typing.List[str] = None,
                                  attachments: typing.List[dict] = None) -> ASYNC_RESPONSE:
        if not (content or embeds or files or sticker_ids):
            raise ValueError("either content or embed or files or sticker_ids must be passed.")
        payload_json = {}
        form = aiohttp.FormData()
        if content:
            payload_json["content"] = content
        if embeds:
            payload_json["embeds"] = embeds
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
        if sticker_ids:
            payload_json["sticker_ids"] = sticker_ids
        if attachments:
            payload_json["attachments"] = attachments
        form.add_field("payload_json", json.dumps(payload_json), content_type="application/json")
        if files is not None:
            for x in range(len(files)):
                name = f"file{x if len(files) > 1 else ''}"
                sel = files[x]
                f = sel.read()
                form.add_field(name, f, filename=sel.name, content_type="application/octet-stream")
        return self.request(f"/channels/{channel_id}/messages", "POST", form)

    def edit_message_with_files(self,
                                channel_id,
                                message_id,
                                content: str = EmptyObject,
                                embeds: typing.List[dict] = EmptyObject,
                                flags: int = EmptyObject,
                                files: typing.List[io.FileIO] = EmptyObject,
                                allowed_mentions: dict = EmptyObject,
                                attachments: typing.List[dict] = EmptyObject,
                                components: typing.List[dict] = EmptyObject) -> ASYNC_RESPONSE:
        payload_json = {}
        form = aiohttp.FormData()
        if content is not EmptyObject:
            payload_json["content"] = content
        if embeds is not EmptyObject:
            payload_json["embeds"] = embeds
        if flags is not EmptyObject:
            payload_json["flags"] = flags
        if allowed_mentions is not EmptyObject:
            payload_json["allowed_mentions"] = allowed_mentions
        if attachments is not EmptyObject:
            payload_json["attachments"] = attachments
        if components is not EmptyObject:
            payload_json["components"] = components
        form.add_field("payload_json", json.dumps(payload_json), content_type="application/json")
        if files is not EmptyObject:
            for x in range(len(files)):
                name = f"file{x if len(files) > 1 else ''}"
                sel = files[x]
                f = sel.read()
                form.add_field(name, f, filename=sel.name, content_type="application/octet-stream")
        return self.request(f"/channels/{channel_id}/messages/{message_id}", "PATCH", form)

    def create_guild_sticker(self, guild_id, name: str, description: str, tags: str, file: io.FileIO, reason: str = None) -> ASYNC_RESPONSE:
        form = aiohttp.FormData()
        form.add_field("name", name)
        form.add_field("description", description)
        form.add_field("tags", tags)
        form.add_field("file", file, filename=file.name, content_type="application/octet-stream")
        return self.request(f"/guilds/{guild_id}/stickers", "POST", form, reason_header=reason)

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
                                   components: typing.List[dict] = None,
                                   attachments: typing.List[dict] = None,
                                   flags: int = None) -> ASYNC_RESPONSE:
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
        if components is not None:
            payload_json["components"] = components
        if attachments is not None:
            payload_json["attachments"] = attachments
        if flags is not None:
            payload_json["flags"] = flags
        params = {}
        if wait is not None:
            params["wait"] = "true" if wait else "false"
        if thread_id is not None:
            params["thread_id"] = thread_id
        form.add_field("payload_json", json.dumps(payload_json), content_type="application/json")
        if files is not None:
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
                             content: str = EmptyObject,
                             embeds: typing.List[dict] = EmptyObject,
                             files: typing.List[io.FileIO] = EmptyObject,
                             allowed_mentions: dict = EmptyObject,
                             attachments: typing.List[dict] = EmptyObject,
                             components: typing.List[dict] = EmptyObject) -> ASYNC_RESPONSE:
        payload_json = {}
        form = aiohttp.FormData()
        if content is not EmptyObject:
            payload_json["content"] = content
        if embeds is not EmptyObject:
            payload_json["embeds"] = embeds
        if allowed_mentions is not EmptyObject:
            payload_json["allowed_mentions"] = allowed_mentions
        if attachments is not EmptyObject:
            payload_json["attachments"] = attachments
        if components is not EmptyObject:
            payload_json["components"] = components
        form.add_field("payload_json", json.dumps(payload_json), content_type="application/json")
        if files is not EmptyObject:
            for x in range(len(files)):
                name = f"file{x if len(files) > 1 else ''}"
                sel = files[x]
                f = sel.read()
                form.add_field(name, f, filename=sel.name, content_type="application/octet-stream")
        return self.request(f"/webhooks/{webhook_id}/{webhook_token}/messages/{message_id}", "PATCH", form)

    async def download(self, url) -> bytes:
        async with self.session.get(url) as resp:
            if resp.status == 200:
                return await resp.read()
            else:
                raise exception.DownloadFailed(url, resp.status, await resp.read())

    @classmethod
    def create(cls,
               token: str,
               loop: asyncio.AbstractEventLoop = None,
               session: aiohttp.ClientSession = None,
               default_retry: int = 3) -> "AsyncHTTPRequest":
        return cls(token, loop, session, default_retry)
