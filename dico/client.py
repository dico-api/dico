import io
import sys
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
from .model import Intents, Channel, Message, MessageReference, AllowedMentions, Snowflake, Embed, Attachment, Application, Activity, Overwrite, Emoji, User


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

    def request_channel(self, channel: typing.Union[int, str, Snowflake, Channel]):
        channel = self.http.request_channel(int(channel))
        if isinstance(channel, dict):
            channel = Channel.create(self, channel)
        return channel

    def modify_guild_channel(self,
                             channel: typing.Union[int, str, Snowflake, Channel],
                             *,
                             name: str = None,
                             channel_type: int = None,
                             position: int = None,
                             topic: str = None,
                             nsfw: bool = None,
                             rate_limit_per_user: int = None,
                             bitrate: int = None,
                             user_limit: int = None,
                             permission_overwrites: typing.List[Overwrite] = None,
                             parent: typing.Union[int, str, Snowflake, Channel] = None,
                             rtc_region: str = None,
                             video_quality_mode: int = None):
        if permission_overwrites:
            permission_overwrites = [x.to_dict() for x in permission_overwrites]
        if parent:
            parent = int(parent)
        channel = self.http.modify_guild_channel(int(channel), name, channel_type, position, topic, nsfw, rate_limit_per_user,
                                                 bitrate, user_limit, permission_overwrites, parent, rtc_region, video_quality_mode)
        if isinstance(channel, dict):
            channel = Channel.create(self, channel)
        return channel

    def modify_group_dm_channel(self, channel: typing.Union[int, str, Snowflake, Channel], *, name: str = None, icon: bin = None):
        channel = self.http.modify_group_dm_channel(int(channel), name, icon)
        if isinstance(channel, dict):
            channel = Channel.create(self, channel)
        return channel

    def modify_thread_channel(self,
                              channel: typing.Union[int, str, Snowflake, Channel], *,
                              name: str = None,
                              archived: bool = None,
                              auto_archive_duration: int = None,
                              locked: bool = None,
                              rate_limit_per_user: int = None):
        channel = self.http.modify_thread_channel(int(channel), name, archived, auto_archive_duration, locked, rate_limit_per_user)
        if isinstance(channel, dict):
            channel = Channel.create(self, channel)
        return channel

    def delete_channel(self, channel: typing.Union[int, str, Snowflake, Channel]):
        return self.http.delete_channel(int(channel))

    def request_channel_messages(self,
                                 channel: typing.Union[int, str, Snowflake, Channel], *,
                                 around: typing.Union[int, str, Snowflake, Message] = None,
                                 before: typing.Union[int, str, Snowflake, Message] = None,
                                 after: typing.Union[int, str, Snowflake, Message] = None,
                                 limit: int = 50):
        messages = self.http.request_channel_messages(int(channel), around and str(int(around)), before and str(int(before)), after and str(int(after)), limit)
        # This looks unnecessary, but this is to ensure they are all numbers.
        if isinstance(messages, list):
            messages = [Message.create(self, x) for x in messages]
        return messages

    def request_channel_message(self, channel: typing.Union[int, str, Snowflake, Channel], message: typing.Union[int, str, Snowflake, Message]):
        message = self.http.request_channel_message(int(channel), int(message))
        if isinstance(message, dict):
            message = Message.create(self, channel)
        return message

    def create_message(self,
                       channel: typing.Union[int, str, Snowflake, Channel],
                       content: str = None,
                       *,
                       embed: typing.Union[Embed, dict] = None,
                       file: typing.Union[io.FileIO, pathlib.Path, str] = None,
                       files: typing.List[typing.Union[io.FileIO, pathlib.Path, str]] = None,
                       tts: bool = False,
                       allowed_mentions: typing.Union[AllowedMentions, dict] = None,
                       message_reference: typing.Union[Message, MessageReference, dict] = None) -> typing.Union[Message, typing.Coroutine[dict, Message, dict]]:
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
        :return: Union[:class:`.model.channel.Message`, Coroutine[dict]]
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
        if _all_men and not isinstance(_all_men, dict):
            _all_men = _all_men.to_dict()
        if embed and not isinstance(embed, dict):
            embed = embed.to_dict()
        if message_reference and not isinstance(message_reference, dict):
            message_reference = message_reference.to_dict()
        params = {"channel_id": int(channel),
                  "content": content,
                  "embed": embed,
                  "nonce": None,  # What does this do tho?
                  "message_reference": message_reference,
                  "tts": tts,
                  "allowed_mentions": _all_men}
        if files:
            params["files"] = files
        try:
            msg = self.http.create_message_with_files(**params) if files else self.http.create_message(**params)
            if isinstance(msg, dict):
                msg = Message.create(self, msg)
            return msg
        finally:
            if files:
                [x.close() for x in files if not x.closed]

    def edit_message(self,
                     channel: typing.Union[int, str, Snowflake, Channel],
                     message: typing.Union[int, str, Snowflake, Message],
                     *,
                     content: str = None,
                     embed: typing.Union[Embed, dict] = None,
                     allowed_mentions: typing.Union[AllowedMentions, dict] = None,
                     attachments: typing.List[typing.Union[Attachment, dict]] = None) -> typing.Union[Message, typing.Coroutine[dict, Message, dict]]:
        _all_men = allowed_mentions or self.default_allowed_mentions
        if _all_men and not isinstance(_all_men, dict):
            _all_men = _all_men.to_dict()
        if embed and not isinstance(embed, dict):
            embed = embed.to_dict()
        _att = []
        if attachments:
            for x in attachments:
                if not isinstance(x, dict):
                    x = x.to_dict()
                _att.append(x)
        params = {"channel_id": int(channel),
                  "message_id": int(message),
                  "content": content,
                  "embed": embed,
                  "flags": None,
                  "allowed_mentions": _all_men,
                  "attachments": _att}
        msg = self.http.edit_message(**params)
        if isinstance(msg, dict):
            msg = Message.create(self, msg)
        return msg

    def delete_message(self,
                       channel: typing.Union[int, str, Snowflake, Channel],
                       message: typing.Union[int, str, Snowflake, Message]):
        return self.http.delete_message(int(channel), int(message))

    def create_reaction(self,
                        channel: typing.Union[int, str, Snowflake, Channel],
                        message: typing.Union[int, str, Snowflake, Message],
                        emoji: typing.Union[str, Emoji]):
        if isinstance(emoji, Emoji):
            emoji = emoji.name if not emoji.id else f"{emoji.name}:{emoji.id}"
        elif emoji.startswith("<") and emoji.endswith(">"):
            emoji = emoji.lstrip("<").rstrip(">")
        return self.http.create_reaction(int(channel), int(message), emoji)

    def delete_reaction(self,
                        channel: typing.Union[int, str, Snowflake, Channel],
                        message: typing.Union[int, str, Snowflake, Message],
                        emoji: typing.Union[str, Emoji],
                        user: typing.Union[int, str, Snowflake, User] = "@me"):
        if isinstance(emoji, Emoji):
            emoji = emoji.name if not emoji.id else f"{emoji.name}:{emoji.id}"
        elif emoji.startswith("<") and emoji.endswith(">"):
            emoji = emoji.lstrip("<").rstrip(">")
        return self.http.delete_reaction(int(channel), int(message), emoji, int(user) if user != "@me" else user)

    @property
    def has_cache(self):
        return hasattr(self, "cache")


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
    :ivar application: :class.model.gateway.Application: of the client.
    """

    def __init__(self,
                 token: str, *,
                 intents: Intents = Intents.no_privileged(),
                 default_allowed_mentions: AllowedMentions = None,
                 loop=None,
                 cache: bool = True):
        self.loop = loop or asyncio.get_event_loop()
        super().__init__(token, base=AsyncHTTPRequest, default_allowed_mentions=default_allowed_mentions, loop=loop)
        self.token = token
        self.__use_cache = cache
        self.cache = CacheContainer() if self.__use_cache else None  # The reason only supporting caching with WS is to ensure up-to-date object.
        self.__ws_class = WebSocketClient
        self.intents = intents
        self.ws: typing.Union[None, WebSocketClient] = None
        self.events = EventHandler(self)
        self.application: typing.Union[None, Application] = None

        # Custom events dispatch
        # self.events.add("MESSAGE_CREATE", lambda x: self.events.dispatch("MESSAGE", x.message))

    def on_(self, name: str = None, meth=None):
        """
        Adds new event listener.

        Example:

        .. code-block:: python

            # These 4 are equivalent.

            @client.on_("message_create")
            async def on_message_create(message):
                ...

            @client.on_("MESSAGE_CREATE")
            async def on_message_create_two(message):
                ...

            @client.on_()
            async def message_create(message):
                ...

            async def message_create_another(message):
                ...

            client.on_("MESSAGE_CREATE", message_create_another)

        :param name: Name of the event. Case-insensitive. Default name of the function.
        :param meth: Method or Coroutine, if you don't want to use as decorator.
        """
        def wrap(func=None):
            func = func or meth
            self.events.add(name.upper() if name else func.__name__.upper().lstrip("ON_"), func)
            return func
        return wrap

    async def wait(self, event_name: str, timeout: float = None, check: typing.Callable = None):
        raise NotImplementedError

    @property
    def on(self):
        return self.on_

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
        if self.has_cache:
            return self.cache.get

    @property
    def get_user(self):
        """Gets user from cache. Alias of ``.cache.get_storage("user").get``."""
        if self.has_cache:
            return self.cache.get_storage("user").get

    @property
    def get_guild(self):
        """Gets guild from cache. Alias of ``.cache.get_storage("guild").get``."""
        if self.has_cache:
            return self.cache.get_storage("guild").get

    @property
    def get_channel(self):
        """Gets channel from cache. Alias of ``.cache.get_storage("channel").get``."""
        if self.has_cache:
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
            print("Detected KeyboardInterrupt, exiting...", file=sys.stderr)
        except Exception as ex:
            traceback.print_exc()
        finally:
            await self.ws.close()
            await self.http.close()

    async def update_presence(self, *, since: int = None, activities: typing.List[typing.Union[Activity, dict]], status: str = "online", afk: bool = False):
        activities = [x.to_dict() if not isinstance(x, dict) else x for x in activities]
        return await self.ws.update_presence(since, activities, status, afk)

    async def request_channel(self, channel: typing.Union[int, str, Snowflake, Channel]) -> Channel:
        return Channel.create(self, await super().request_channel(channel))

    async def modify_guild_channel(self, *args, **kwargs) -> Channel:
        return Channel.create(self, await super().modify_guild_channel(*args, **kwargs))

    async def modify_group_dm_channel(self, *args, **kwargs) -> Channel:
        return Channel.create(self, await super().modify_group_dm_channel(*args, **kwargs))

    async def modify_thread_channel(self, *args, **kwargs) -> Channel:
        return Channel.create(self, await super().modify_thread_channel(*args, **kwargs))

    async def request_channel_messages(self, *args, **kwargs) -> typing.List[Message]:
        return [Message.create(self, x) for x in await super().request_channel_messages(*args, **kwargs)]

    async def request_channel_message(self, *args, **kwargs) -> Message:
        return Message.create(self, await super().request_channel_message(*args, **kwargs))

    async def create_message(self, *args, **kwargs) -> Message:
        return Message.create(self, await super().create_message(*args, **kwargs))

    async def edit_message(self, *args, **kwargs) -> Message:
        return Message.create(self, await super().edit_message(*args, **kwargs))

    @property
    def has_cache(self):
        return self.__use_cache

    def run(self):
        """
        Runs client. Actually this is sync function wrapping :meth:`.start`.

        .. warning::
            This must be placed at the end of the code.
        """
        self.loop.run_until_complete(self.start())
