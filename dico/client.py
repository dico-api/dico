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
    """
    REST API handling client.

    .. note::
        If you chose to use async request handler, all request functions will return coroutine which will return raw instance.

    :param token: Token of the client.
    :param base: HTTP request handler to use. Must inherit :class:`.base.http.HTTPRequestBase`.
    :param default_allowed_mentions: Default :class:`.model.channel.AllowedMentions` object to use. Default None.
    :param **http_options: Options of HTTP request handler.

    :ivar http: HTTP request client.
    :ivar default_allowed_mentions: Default :class:`.model.channel.AllowedMentions` object of the API client.
    """

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
                       message_reference: typing.Union[Message, MessageReference] = None) -> typing.Union[Message, typing.Coroutine[dict]]:
        """
        Sends message create request to API.

        .. note::
            - FileIO object passed to ``file`` or ``files`` parameter will be automatically closed when requesting,
              therefore it is recommended to pass file path.

        .. warning::
            - You must pass at least one of ``content`` or ``embed`` or ``file`` or ``files`` parameter.
            - You can't use ``file`` and ``files`` at the same time.

        :param channel: Channel to create message. Accepts both :class:`.model.channel.Channel` and channel ID.
        :param content: Content of the message.
        :param embed: Embed of the message.
        :param file: File of the message.
        :param files: Files of the message.
        :param tts: Whether to speak message.
        :param allowed_mentions: :class:`.model.channel.AllowedMentions` to use for this request.
        :param message_reference: Message to reply.
        :return: Union[:class:`.model.channel.Message`, typing.Coroutine[dict]]
        """
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
    """
    Client with async request handler and websocket support.

    :param token: Token of the client.
    :param intents: Intents to use. Default everything except privileged.
    :param default_allowed_mentions: Default :class:`.model.channel.AllowedMentions` object to use. Default None.
    :param loop: asyncio Event loop object to use. Default automatic.

    :ivar http: HTTP request client.
    :ivar default_allowed_mentions: Default :class:`.model.channel.AllowedMentions` object of the client.
    :ivar loop: asyncio Event loop object of the client.
    :ivar cache: :class:`.cache.Intents` of the client.
    :ivar intents: :class:`.model.gateway.Intents` of the client.
    :ivar ws: Websocket client of the client.
    :ivar events: :class:`.handler.EventHandler` of the client.
    """

    def __init__(self,
                 token: str, *,
                 intents: Intents = Intents.no_privileged(),
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

        Example:

        .. code-block:: python

            # These 3 are equivalent.

            @client.on_("message_create")
            async def on_message_create(message_create):
                ...

            @client.on_("MESSAGE_CREATE")
            async def on_message_create_two(message_create):
                ...

            @client.on_()
            async def message_create(message_create):
                ...

        :param name: Name of the event. Case-insensitive. Default name of the function.
        """
        def wrap(func):
            self.events.add(name.upper(), func)
            return func
        return wrap

    def dispatch(self, name, *args, **kwargs):
        """
        Dispatches new event.

        :param name: Name of the event.
        :param args: Arguments of the event.
        :param kwargs: Keyword arguments of the client.
        """
        [self.loop.create_task(utils.safe_call(x(*args, **kwargs))) for x in self.events.get(name.upper())]

    @property
    def get(self):
        """Alias of ``.cache.get``."""
        return self.cache.get

    @property
    def get_user(self):
        """Gets user from cache. Alias of ``.cache.get_storage("user").get``."""
        return self.cache.get_storage("user").get

    @property
    def get_guild(self):
        """Gets guild from cache. Alias of ``.cache.get_storage("guild").get``."""
        return self.cache.get_storage("guild").get

    @property
    def get_channel(self):
        """Gets channel from cache. Alias of ``.cache.get_storage("channel").get``."""
        return self.cache.get_storage("channel").get

    async def start(self):
        """
        Starts websocket connection and clears every connections after stopping due to error or KeyboardInterrupt.

        .. warning::
            You can call this only once.
        """
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

    async def create_message(self, *args, **kwargs) -> Message:
        """
        Sends message create request to API.

        .. note::
            - FileIO object passed to ``file`` or ``files`` parameter will be automatically closed when requesting,
              therefore it is recommended to pass file path.

        .. warning::
            - You must pass at least one of ``content`` or ``embed`` or ``file`` or ``files`` parameter.
            - You can't use ``file`` and ``files`` at the same time.

        :param channel: Channel to create message. Accepts both :class:`.model.channel.Channel` and channel ID.
        :param content: Content of the message.
        :param embed: Embed of the message.
        :param file: File of the message.
        :param files: Files of the message.
        :param tts: Whether to speak message.
        :param allowed_mentions: :class:`.model.channel.AllowedMentions` to use for this request.
        :param message_reference: Message to reply.
        :return: :class:`.model.channel.Message`
        """
        return Message(self, await super().create_message(*args, **kwargs))

    def run(self):
        """
        Runs client. Actually this is sync function wrapping :meth:`.start`.

        .. warning::
            This must be placed at the end of the code.
        """
        self.loop.run_until_complete(self.start())
