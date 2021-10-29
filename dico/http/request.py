import io
import json
import time
import typing
import logging
import requests
from .. import exception, __version__
from ..base.http import HTTPRequestBase, EmptyObject, _R

RESPONSE = _R


class HTTPRequest(HTTPRequestBase):
    def __init__(self, token: str, default_retry: int = 3):
        self.token = token
        self.default_retry = default_retry
        self.logger: logging.Logger = logging.getLogger("dico.http")

    def request(self,
                route: str,
                meth: str,
                body: typing.Any = None,
                *,
                is_json: bool = False,
                reason_header: str = None,
                retry: int = 3,
                **kwargs) -> RESPONSE:
        headers = {"Authorization": f"Bot {self.token}", "User-Agent": f"DiscordBot (https://github.com/dico-api/dico, {__version__})"}
        if meth not in ["GET"] and body is not None:
            if is_json:
                headers["Content-Type"] = "application/json"
                body = json.dumps(body)
            kwargs["data"] = body
        if reason_header is not None:
            headers["X-Audit-Log-Reason"] = reason_header
        code = 429  # Empty code in case of rate limit fail.
        resp = {}   # Empty resp in case of rate limit fail.
        retry = (retry if retry > 0 else 1) if retry is not None else self.default_retry
        for x in range(retry):
            response = requests.request(meth, self.BASE_URL + route, headers=headers, **kwargs)
            resp = (response.json() if response.headers.get("Content-Type") == "application/json" else response.text) if response.status_code != 204 else None
            code = response.status_code
            self.logger.debug(f"{route}: {meth} request - {code}")
            if 200 <= code < 300:
                return resp
            elif code == 400:
                raise exception.BadRequest(route, code, resp)
            elif code == 403:
                raise exception.Forbidden(route, code, resp)
            elif code == 404:
                raise exception.NotFound(route, code, resp)
            elif code == 429:
                wait_sec = float(resp["retry_after"])
                self.logger.warning(f"Rate limited, waiting for {wait_sec} second{'s' if wait_sec == 1 else ''}...")
                time.sleep(wait_sec)
                continue
            elif 500 <= code < 600:
                raise exception.DiscordError(route, code, resp)
            else:
                raise exception.Unknown(route, code, resp)
        raise exception.RateLimited(route, code, resp)

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
                                  attachments: typing.List[dict] = None) -> RESPONSE:
        if not (content or embeds or files or sticker_ids):
            raise ValueError("either content or embed or files or sticker_ids must be passed.")
        payload_json = {}
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
        _files = {"payload_json": (None, json.dumps(payload_json), "application/json")}
        if files is not None:
            for x in range(len(files)):
                name = f"file{x if len(files) > 1 else ''}"
                sel = files[x]
                f = sel.read()
                _files[name] = (sel.name, f, "application/octet-stream")
        return self.request(f"/channels/{channel_id}/messages", "POST", files=_files)

    def edit_message_with_files(self,
                                channel_id,
                                message_id,
                                content: str = EmptyObject,
                                embeds: typing.List[dict] = EmptyObject,
                                flags: int = EmptyObject,
                                files: typing.List[io.FileIO] = EmptyObject,
                                allowed_mentions: dict = EmptyObject,
                                attachments: typing.List[dict] = EmptyObject,
                                components: typing.List[dict] = EmptyObject) -> RESPONSE:
        payload_json = {}
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
        _files = {"payload_json": (None, json.dumps(payload_json), "application/json")}
        if files is not EmptyObject:
            for x in range(len(files)):
                name = f"file{x if len(files) > 1 else ''}"
                sel = files[x]
                f = sel.read()
                _files[name] = (sel.name, f, "application/octet-stream")
        return self.request(f"/channels/{channel_id}/messages/{message_id}", "PATCH", files=_files)

    def create_guild_sticker(self,
                             guild_id,
                             name: str,
                             description: str,
                             tags: str,
                             file: io.FileIO,
                             reason: str = None) -> RESPONSE:
        data = {"name": name, "description": description, "tags": tags}
        file = {"file": (file.name, file, "application/octet-stream")}
        return self.request(f"/guilds/{guild_id}/stickers", "POST", data, files=file, reason_header=reason)

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
                                   flags: int = None) -> RESPONSE:
        payload_json = {}
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
        _files = {"payload_json": (None, json.dumps(payload_json), "application/json")}
        if files is not None:
            for x in range(len(files)):
                name = f"file{x if len(files) > 1 else ''}"
                sel = files[x]
                f = sel.read()
                _files[name] = (sel.name, f, "application/octet-stream")
        return self.request(f"/webhooks/{webhook_id}/{webhook_token}", "POST", files=_files, params=params)

    def edit_webhook_message(self, webhook_id, webhook_token, message_id, content: str = EmptyObject,
                             embeds: typing.List[dict] = EmptyObject, files: typing.List[io.FileIO] = EmptyObject,
                             allowed_mentions: dict = EmptyObject, attachments: typing.List[dict] = EmptyObject,
                             components: typing.List[dict] = EmptyObject) -> RESPONSE:
        payload_json = {}
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
        _files = {"payload_json": (None, json.dumps(payload_json), "application/json")}
        if files is not None:
            for x in range(len(files)):
                name = f"file{x if len(files) > 1 else ''}"
                sel = files[x]
                f = sel.read()
                _files[name] = (sel.name, f, "application/octet-stream")
        return self.request(f"/webhooks/{webhook_id}/{webhook_token}/messages/{message_id}", "PATCH", files=_files)

    def download(self, url) -> RESPONSE:
        resp = requests.get(url)
        if resp.status_code == 200:
            return resp.raw
        else:
            raise exception.DownloadFailed(url, resp.status_code, resp.raw)

    @classmethod
    def create(cls, token, *args, **kwargs) -> "HTTPRequest":
        return cls(token, *args, **kwargs)
