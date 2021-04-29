import io
import typing
import asyncio
import pathlib
import traceback
from . import utils
from .base.http import HTTPRequestBase
from .http.async_http import AsyncHTTPRequest
from .ws.websocket import WebSocketClient
from .cache import CacheContainer
from .handler import EventHandler
from .model import Intents, Channel, Message, MessageReference, AllowedMentions, Snowflake


class APIClient:
    def __init__(self, token, *, base: typing.Type[HTTPRequestBase], default_allowed_mentions: AllowedMentions = None, **http_options):
        self.http = base.create(token, **http_options)
        self.default_allowed_mentions = default_allowed_mentions

    def create_message(self,
                       channel: typing.Union[int, str, Channel],
                       content: str = None,
                       *,
                       embed = None,
                       file: typing.Union[io.FileIO, pathlib.Path, str] = None,
                       files: typing.List[typing.Union[io.FileIO, pathlib.Path, str]] = None,
                       tts: bool = False,
                       allowed_mentions: typing.Union[AllowedMentions, dict] = None,
                       message_reference: typing.Union[Message, MessageReference] = None):
        if files and file:
            raise
        if file:
            files = [file]
        if files:
            for x in range(len(files)):
                sel = files[x]
                if not isinstance(sel, io.FileIO):
                    files[x] = open(sel, "rb")
        if isinstance(message_reference, Message):
            message_reference = MessageReference.from_message(message_reference)
        _all_men = allowed_mentions or self.default_allowed_mentions
        if _all_men:
            if not isinstance(_all_men, dict):
                _all_men = _all_men.to_dict()
        params = {"channel_id": int(channel),
                  "content": content,
                  "embed": embed,
                  "nonce": None,  # What does this do tho?
                  "message_reference": message_reference.to_dict() if message_reference else None,
                  "tts": tts,
                  "allowed_mentions": _all_men}
        if files:
            params["files"] = files
        try:
            msg = self.http.create_message_with_files(**params) if files else self.http.create_message(**params)
            if isinstance(msg, dict):
                msg = Message(self, msg)
            return msg
        finally:
            if files:
                [x.close() for x in files if not x.closed]


class Client(APIClient):
    def __init__(self,
                 token: str, *,
                 intents=Intents.no_privileged(),
                 default_allowed_mentions: AllowedMentions = None,
                 loop=None):
        self.loop = loop or asyncio.get_event_loop()
        super().__init__(token, base=AsyncHTTPRequest, default_allowed_mentions=default_allowed_mentions, loop=loop)
        self.token = token
        self.cache = CacheContainer()  # The reason only supporting caching with WS is to ensure up-to-date object.
        self.__ws_class = WebSocketClient
        self.intents = intents
        self.ws: typing.Union[None, WebSocketClient] = None
        self.events = EventHandler(self)

        # Custom events dispatch
        # self.events.add("MESSAGE_CREATE", lambda x: self.events.dispatch("MESSAGE", x.message))

    def on_(self, name: str = None):
        """
        Adds new event listener.
        :param name: Name of the event. Case-insensitive. Default name of the function.
        """
        def wrap(func):
            self.events.add(name.upper(), func)
            return func
        return wrap

    def dispatch(self, name, *args, **kwargs):
        [self.loop.create_task(utils.safe_call(x(*args, **kwargs))) for x in self.events.get(name.upper())]

    @property
    def get(self):
        """Alias of ``Client.cache.get``."""
        return self.cache.get

    @property
    def get_user(self):
        return self.cache.get_storage("user").get

    @property
    def get_guild(self):
        return self.cache.get_storage("guild").get

    @property
    def get_channel(self):
        return self.cache.get_storage("channel").get

    async def start(self):
        self.ws = await self.__ws_class.connect(self.http, self.intents, self.events)
        try:
            await self.ws.run()
        except KeyboardInterrupt:
            pass
        except Exception as ex:
            traceback.print_exc()
        finally:
            await self.ws.close()
            await self.http.close()

    async def create_message(self, *args, **kwargs):
        return Message(self, await super().create_message(*args, **kwargs))

    def run(self):
        self.loop.run_until_complete(self.start())
