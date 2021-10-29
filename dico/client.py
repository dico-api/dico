import sys
import typing
import asyncio
import logging
import traceback
from contextlib import suppress

from . import utils
from .api import APIClient
from .http.async_http import AsyncHTTPRequest
from .ws.websocket import WebSocketClient
from .cache import CacheContainer
from .exception import WebsocketClosed
from .handler import EventHandler
from .model import Intents, AllowedMentions, Snowflake, Activity, Guild, Channel
from .utils import get_shard_id


class Client(APIClient):
    """
    Client with async request handler and websocket connection.

    :param str token: Token of the client.
    :param Intents intents: Intents to use. Default everything except privileged.
    :param Optional[AllowedMentions] default_allowed_mentions: Default allowed mentions object to use. Default None.
    :param Optional[asyncio.AbstractEventLoop] loop: asyncio Event loop object to use. Default automatic.
    :param bool cache: Whether to enable caching. Default True.
    :param application_id: Application ID if needed.
    :type application_id: Optional[Union[int, str, Snowflake]]
    :param bool monoshard: Whether to mono-shard this bot.
    :param Optional[int] shard_count: Count of shards to launch, if monoshard is True.
    :param Optional[int] shard_id: Shard ID of the client. This is not recommended.
    :param cache_max_sizes: Max sizes of the cache per types. Message limit is set to 1000 by default.

    :ivar AsyncHTTPRequest ~.http: HTTP request client.
    :ivar Optional[AllowedMentions] ~.default_allowed_mentions: Default :class:`.model.channel.AllowedMentions` object of the client.
    :ivar asyncio.AbstractEventLoop ~.loop: asyncio Event loop object of the client.
    :ivar str ~.token: Application token of the client.
    :ivar Optional[CacheContainer] ~.cache: Cache container of the client.
    :ivar Intents ~.intents: Intents of the client.
    :ivar Optional[WebSocketClient] ~.ws: Websocket client of the client.
    :ivar EventHandler ~.events: Event handler of the client.
    :ivar Optional[Application] ~.application: Application object of the client.
    :ivar Optional[Snowflake] ~.application_id: ID of the application. Can be ``None`` if Ready event is not called, and if it is, you must pass parameter application_id for all methods that has it.
    :ivar bool ~.monoshard: Whether mono-sharding is enabled.
    :ivar Optional[int] ~.shard_count: Current shard count of the bot.
    """

    def __init__(self,
                 token: str, *,
                 intents: Intents = Intents.no_privileged(),
                 default_allowed_mentions: typing.Optional[AllowedMentions] = None,
                 loop: typing.Optional[asyncio.AbstractEventLoop] = None,
                 cache: bool = True,
                 application_id: typing.Optional[Snowflake.TYPING] = None,
                 monoshard: bool = False,
                 shard_count: typing.Optional[int] = None,
                 shard_id: typing.Optional[int] = None,
                 **cache_max_sizes: int):
        cache_max_sizes.setdefault("message", 1000)
        self.loop: asyncio.AbstractEventLoop = loop or asyncio.get_event_loop()
        super().__init__(token, base=AsyncHTTPRequest, default_allowed_mentions=default_allowed_mentions, loop=loop, application_id=application_id)
        self.token: str = token
        self.__use_cache = cache
        self.cache: typing.Optional[CacheContainer] = CacheContainer(**cache_max_sizes) if self.__use_cache else None
        # The reason only supporting caching with WS is to ensure up-to-date object.
        self.__ws_class = WebSocketClient
        self.intents: Intents = intents
        self.ws: typing.Optional[WebSocketClient] = None
        self.events: EventHandler = EventHandler(self)
        self.__wait_futures = {}
        self.__ready_future = asyncio.Future()
        self.monoshard: bool = monoshard
        self.shard_count: typing.Optional[int] = shard_count
        self.logger = logging.getLogger("dico.client")
        self.__shards = {} if self.monoshard else None
        self.__shard_id = shard_id
        self.__shard_ids = []
        self.__shard_ids_ready = []
        self.__unavailable_guilds = set()
        self.__compress = False
        self.__reconnect_on_unknown_disconnect = False

        # Internal events dispatch
        self.events.add("READY", self.__ready)
        self.events.add("VOICE_STATE_UPDATE", self.__voice_state_update)

    def __ready(self, ready):
        self.application_id = Snowflake(ready.application["id"])
        if not self.__shards:
            if not self.__ready_future.done():
                self.__ready_future.set_result(True)
            self.__unavailable_guilds = set(x["id"] for x in ready.guilds)
        else:
            if ready.shard_id not in self.__shard_ids_ready:
                self.__shard_ids_ready.append(ready.shard_id)
                self.__unavailable_guilds.update([x["id"] for x in ready.guilds])
            if self.__shard_ids == self.__shard_ids_ready:
                self.__shard_ids_ready = []
                if not self.__ready_future.done():
                    self.__ready_future.set_result(True)
                self.dispatch("shards_ready")

    def __voice_state_update(self, voice_state):
        if self.has_cache:
            user = self.get(voice_state.user_id)
            if user:
                user.set_voice_state(voice_state)

    def on_(self, name: typing.Optional[str] = None, meth: typing.Optional[typing.Union[typing.Callable, typing.Coroutine]] = None) -> typing.Any:
        """
        Adds new event listener. This can be used as decorator or function.

        Example:

        .. code-block:: python

            @client.on_("message_create")  # Also can use "@client.on(...)" or "@client.on_message_create", and event name is default name of the function.
            async def on_message_create(message: dico.Message):
                ...

            def initial_actions(ready: dico.Ready):  # Both coroutine and normal function can be used.
                ...
            client.on_("ready", initial_actions)  # Alias is "client.on(..., ...)"

            client.on_ready = lambda r: print("Ready!")  # You may also directly assign event.


        :param Optional[str] name: Name of the event. Case-insensitive. Default name of the function.
        :param meth: Method or Coroutine, if you don't want to use as decorator.
        :type meth: Optional[Union[Callable, Coroutine]]
        """
        def wrap(func=None):
            func = func or meth
            self.events.add(name.upper() if name else func.__name__.upper().lstrip("ON_"), func)
            return func
        return wrap if meth is None else wrap()

    @property
    def on(self):
        """Alias of :meth:`.on_`"""
        return self.on_

    def wait(self, event_name: str, timeout: typing.Optional[float] = None, check: typing.Optional[typing.Callable[[typing.Any], bool]] = None) -> typing.Any:
        """
        Waits for the event dispatch.

        :param str event_name: Name of the event. Case insensitive.
        :param Optional[float] timeout: Timeout time in second. If not passed, it will wait forever.
        :param check: Check function of the event. If passed, it will wait until the event result passes the check.
        :type check: Optional[Callable[[Any], bool]]
        :return: Payload of the event.
        :raises TimeoutError: Timeout occurred.
        :raises WebsocketClosed: Websocket is closed, therefore further action could not be performed.
        """
        async def wrap():
            while not self.websocket_closed:
                future = asyncio.Future()
                if event_name.upper() not in self.__wait_futures:
                    self.__wait_futures[event_name.upper()] = []
                self.__wait_futures[event_name.upper()].append(future)
                res = await asyncio.wait_for(future, timeout=None)
                ret = res if len(res) > 1 else res[0]
                if check and check(*res):
                    return ret
                elif not check:
                    return ret
            raise WebsocketClosed
        return asyncio.wait_for(wrap(), timeout=timeout)

    def dispatch(self, name: str, *args: typing.Any):
        """
        Dispatches new event.

        :param str name: Name of the event.
        :param Any args: Arguments of the event.
        """
        [self.loop.create_task(utils.safe_call(x(*args))) for x in self.events.get(name.upper())]
        # [self.__wait_futures[name.upper()].pop(x).set_result(args) for x in range(len(self.__wait_futures.get(name.upper(), [])))]
        """
        for x in range(len(self.__wait_futures.get(name.upper(), []))):
            with suppress(IndexError):  # temporary fix, we might need to use while instead
                fut: asyncio.Future = self.__wait_futures[name.upper()].pop(x)
                if not fut.cancelled():
                    fut.set_result(args)
        """
        tgt = self.__wait_futures.get(name.upper(), [])
        while tgt:
            fut: asyncio.Future = tgt.pop(0)
            if not fut.cancelled():
                fut.set_result(args)

    def get_shard_id(self, guild: Guild.TYPING) -> int:
        """
        Gets shard ID from guild.

        :param guild: Guild to get shard ID.
        :return: ID of the shard.
        """
        if self.__shards:
            return get_shard_id(int(guild), len(self.__shards))

    def get_shard(self, guild: Guild.TYPING) -> typing.Optional[WebSocketClient]:
        """
        Gets shard from guild.

        :param guild: Guild to get shard.
        :return: :class:`.ws.websocket.WebSocketClient`
        """
        if self.__shards:
            shard_id = get_shard_id(int(guild), len(self.__shards))
            return self.__shards.get(shard_id)

    async def wait_ready(self):
        """Waits until bot is ready."""
        if not self.__ready_future.done():
            await self.__ready_future

    @property
    def get(self):
        """
        Alias of ``.cache.get``.

        .. note::
            These shortcuts are also available: ``get_guild``, ``get_channel``, ``get_role``, ``get_user``, ``get_sticker``, ``get_message``
        """
        if self.has_cache:
            return self.cache.get

    async def start(self, reconnect_on_unknown_disconnect: bool = False, compress: bool = False):
        """
        Starts websocket connection.

        .. warning::
            You can call this only once.

        :param bool reconnect_on_unknown_disconnect: Whether to reconnect on unknown websocket error.
        :param bool compress: Whether to enable zlib compress.
        """
        if self.monoshard:
            gateway = await self.request_gateway()
            shard_count = self.shard_count or gateway.shards
            if self.shard_count is None:
                self.shard_count = gateway.shards
            self.__shard_ids = [*range(shard_count)]
            for x in self.__shard_ids:
                ws = await self.__ws_class.connect_without_request(
                    gateway, self.http, self.intents, self.events, reconnect_on_unknown_disconnect, compress, shard=[x, shard_count]
                )
                self.__shards[x] = ws
                await ws.receive_once()
                self.loop.create_task(ws.run())
                await asyncio.sleep(5)
        else:
            maybe_shard = {"shard": [self.__shard_id, self.shard_count]} if self.__shard_id else {}
            self.ws = await self.__ws_class.connect(self.http, self.intents, self.events, reconnect_on_unknown_disconnect, compress, **maybe_shard)
            await self.ws.run()

    async def close(self):
        """Clears all connections and closes session."""
        if self.ws:
            await self.ws.close()
        elif self.__shards:
            for x in self.__shards.values():
                await x.close()
        await self.http.close()  # noqa

    async def update_presence(self, *, since: typing.Optional[int] = None, activities: typing.List[typing.Union[Activity, dict]], status: str = "online", afk: bool = False):
        """
        Updates the bot presence.

        All parameters must be passed as keyword.

        :param Optional[int] since: Time as millisecond when the bot was idle since.
        :param activities: List of activities.
        :type activities: List[Union[Activity, dict]]
        :param str status: Status of the bot. Default ``online``.
        :param bool afk: Whether the bot is AFK.
        """
        activities = [x.to_dict() if not isinstance(x, dict) else x for x in activities]
        if self.ws:
            await self.ws.update_presence(since, activities, status, afk)
        elif self.__shards:
            for x in self.__shards.values():
                await x.update_presence(since, activities, status, afk)

    def update_voice_state(self,
                           guild: Guild.TYPING,
                           channel: typing.Optional[Channel.TYPING] = None,
                           self_mute: bool = False,
                           self_deaf: bool = False):
        """
        Changes the voice state of the bot in guild. (Connecting/Disconnecting from the guild, etc...)

        :param guild: Guild to change presence.
        :param channel: Voice channel to connect. Pass nothing or None to disconnect from the channel.
        :param bool self_mute: Whether the bot is self-muted.
        :param bool self_deaf: Whether the bot is self-deaf.
        """
        if self.ws:
            ws = self.ws
        elif self.__shards:
            ws = self.get_shard(guild)
            if not ws:
                raise AttributeError(f"shard for guild {int(guild)} not found.")
        else:
            raise AttributeError(f"shard for guild {int(guild)} not found.")
        return ws.update_voice_state(str(int(guild)), str(int(channel)) if channel else None, self_mute, self_deaf)

    async def increase_shards(self, number: int = 1, *, auto: bool = False):
        """
        Increases numbers of shards.

        .. warning::
            During this action, client will be offline.

        :param int number: Number of shards to increase. Default 1.
        :param bool auto: Whether to automatically use recommended number. Default False.
        """
        if self.ws:
            raise TypeError("this client is not monosharded.")
        elif self.__shards:
            for x in self.__shards.values():
                await x.close()
        if auto:
            resp = await self.request_gateway()
            self.shard_count = resp.shards
        else:
            self.shard_count += number
        self.loop.create_task(self.start(reconnect_on_unknown_disconnect=self.__reconnect_on_unknown_disconnect, compress=self.__compress))

    @property
    def has_cache(self) -> bool:
        """Whether the caching is enabled."""
        return self.__use_cache

    @property
    def websocket_closed(self) -> bool:
        """Whether the bot is disconnected from the Discord websocket. If the bot is sharded, then it will return whether every shards are available."""
        if self.ws:
            return self.ws.closed
        elif self.__shards:
            return any([x.closed for x in self.__shards.values()])
        return True

    @property
    def shards_closed(self) -> typing.List[bool]:
        """Returns list of whether the shard is closed."""
        if not self.__shards:
            raise TypeError("unable to get shards closed status")
        return [x.closed for x in self.__shards.values()]

    @property
    def guild_count(self) -> typing.Optional[int]:
        """Total count of guilds this bot is in. This may be incorrect since this relies on initial guild count or cached guild count."""
        initial_guild_count = len(self.__unavailable_guilds)
        if self.has_cache:
            return sorted([initial_guild_count, self.cache.get_size("guild")])[-1]
        self.logger.warning("Caching is disabled, showing initial guild count.")
        return initial_guild_count

    @property
    def ping(self) -> float:
        """Websocket ping of the bot. If it is sharded, then it will return average ping between shards."""
        if self.ws:
            return self.ws.ping
        elif self.__shards:
            pings = [x.ping for x in self.__shards.values()]
            return sum(pings) / len(pings)
        else:
            return 0.0

    @property
    def shards(self) -> typing.Optional[typing.Tuple[WebSocketClient]]:
        """Tuple of shards this bot has."""
        return tuple(self.__shards.values()) if self.__shards else None

    def __setattr__(self, key, value):
        if not key.lower().startswith("on_") or key.lower() in ["on", "on_"]:
            return super().__setattr__(key, value)
        event_name = key.lower().lstrip("on_")
        return self.on_(event_name, value)

    def __getattr__(self, item):
        if item.startswith("get_"):
            def wrap(snowflake_id):
                return self.get(snowflake_id, item[4:])  # noqa
            return wrap

        if not item.lower().startswith("on_") or item.lower() in ["on", "on_", "get"]:
            return super().__getattribute__(item)  # Should raise AttributeError or whatever.

        event_name = item.lower().lstrip("on_")

        def deco(func):
            return self.on_(event_name, func)

        return deco

    def run(self, *, reconnect_on_unknown_disconnect: bool = False, compress: bool = False):
        """
        Runs client and clears every connections after stopping due to error or KeyboardInterrupt.

        .. warning::
            This must be placed at the end of the code.

        :param bool reconnect_on_unknown_disconnect: Whether to reconnect on unknown websocket error.
        :param bool compress: Whether to enable zlib compress.
        """
        self.__reconnect_on_unknown_disconnect = self.__reconnect_on_unknown_disconnect
        self.__compress = compress
        try:
            self.loop.create_task(self.start(reconnect_on_unknown_disconnect, compress))
            self.loop.run_forever()
        except KeyboardInterrupt:
            print("Detected KeyboardInterrupt, exiting...", file=sys.stderr)
        except Exception as ex:
            print("Unexpected exception occurred, exiting...", file=sys.stderr)
            traceback.print_exc()
        finally:
            self.loop.run_until_complete(self.close())

    def kill(self):
        """Kills event loop and stops bot."""
        self.loop.stop()
