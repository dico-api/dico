import sys
import typing
import asyncio
import traceback
from contextlib import suppress

from . import utils
from .api import APIClient
from .http.async_http import AsyncHTTPRequest
from .ws.websocket import WebSocketClient
from .cache import CacheContainer
from .exception import WebsocketClosed
from .handler import EventHandler
from .model import Intents, AllowedMentions, Snowflake, Application, Activity, Guild, Channel


class Client(APIClient):
    """
    Client with async request handler and websocket support.

    :param token: Token of the client.
    :param intents: Intents to use. Default everything except privileged.
    :param default_allowed_mentions: Default :class:`.model.channel.AllowedMentions` object to use. Default None.
    :param loop: asyncio Event loop object to use. Default automatic.
    :param application_id: Application ID if needed.

    :ivar http: HTTP request client.
    :ivar default_allowed_mentions: Default :class:`.model.channel.AllowedMentions` object of the client.
    :ivar loop: asyncio Event loop object of the client.
    :ivar cache: :class:`.cache.Intents` of the client.
    :ivar intents: :class:`.model.gateway.Intents` of the client.
    :ivar ws: Websocket client of the client.
    :ivar events: :class:`.handler.EventHandler` of the client.
    :ivar application: :class.model.gateway.Application: of the client.
    :ivar application_id: ID of the application. Can be ``None`` if Ready event is not called, and if it is, you must pass parameter application_id for all methods that has it.
    """

    def __init__(self,
                 token: str, *,
                 intents: Intents = Intents.no_privileged(),
                 default_allowed_mentions: AllowedMentions = None,
                 loop=None,
                 cache: bool = True,
                 application_id: typing.Union[str, int, Snowflake] = None):
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
        self.__wait_futures = {}
        self.application_id = Snowflake.ensure_snowflake(application_id)
        self.__ready_future = asyncio.Future()

        # Internal events dispatch
        self.events.add("READY", self.__ready)
        self.events.add("VOICE_STATE_UPDATE", self.__voice_state_update)

    def __ready(self, ready):
        self.application_id = Snowflake(ready.application["id"])
        if not self.__ready_future.done():
            self.__ready_future.set_result(True)

    def __voice_state_update(self, voice_state):
        if self.has_cache:
            user = self.get(voice_state.user_id)
            if user:
                user.set_voice_state(voice_state)

    def on_(self, name: str = None, meth=None):
        """
        Adds new event listener. This can be used as decorator or function.

        :param name: Name of the event. Case-insensitive. Default name of the function.
        :param meth: Method or Coroutine, if you don't want to use as decorator.
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

    def wait(self, event_name: str, timeout: float = None, check: typing.Callable[[typing.Any], bool] = None):
        """
        Waits for the event dispatch.

        :param event_name: Name of the event. Case insensitive.
        :param timeout: Timeout time in second. If not passed, it will wait forever.
        :param check: Check function of the event. If passed, it will wait until the event result passes the check.
        :return: Payload of the event.
        :raises: TimeoutError - Timeout occurred.
        :raises: WebsocketClosed - Websocket is closed, so waiting is canceled.
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

    def dispatch(self, name, *args):
        """
        Dispatches new event.

        :param name: Name of the event.
        :param args: Arguments of the event.
        """
        [self.loop.create_task(utils.safe_call(x(*args))) for x in self.events.get(name.upper())]
        # [self.__wait_futures[name.upper()].pop(x).set_result(args) for x in range(len(self.__wait_futures.get(name.upper(), [])))]
        for x in range(len(self.__wait_futures.get(name.upper(), []))):
            with suppress(IndexError):  # temporary fix, we might need to use while instead
                fut: asyncio.Future = self.__wait_futures[name.upper()].pop(x)
                if not fut.cancelled():
                    fut.set_result(args)

    async def wait_ready(self):
        if not self.__ready_future.done():
            await self.__ready_future

    @property
    def get(self):
        """Alias of ``.cache.get``."""
        if self.has_cache:
            return self.cache.get

    async def start(self, reconnect_on_unknown_disconnect: bool = False, compress: bool = True):
        """
        Starts websocket connection.

        .. warning::
            You can call this only once.
        """
        self.ws = await self.__ws_class.connect(self.http, self.intents, self.events, reconnect_on_unknown_disconnect, compress)
        await self.ws.run()

    async def close(self):
        """Clears all connections and closes session."""
        await self.ws.close()
        await self.http.close()

    def update_presence(self, *, since: int = None, activities: typing.List[typing.Union[Activity, dict]], status: str = "online", afk: bool = False):
        """
        Updates the bot presence.

        All parameters must be passed as keyword.

        :param since: Time as millisecond when the bot was idle since.
        :param activities: List of activities.
        :param status: Status of the bot.
        :param afk: Whether the bot is AFK.
        """
        activities = [x.to_dict() if not isinstance(x, dict) else x for x in activities]
        return self.ws.update_presence(since, activities, status, afk)

    def update_voice_state(self,
                           guild: typing.Union[int, str, Snowflake, Guild],
                           channel: typing.Union[int, str, Snowflake, Channel] = None,
                           self_mute: bool = False,
                           self_deaf: bool = False):
        """
        Changes the voice state of the bot in guild. (Connecting/Disconnecting from the guild, etc...)

        :param guild: Guild to change presence.
        :param channel: Voice channel to connect. Pass nothing or None to disconnect from the channel.
        :param self_mute: Whether the bot is self-muted.
        :param self_deaf: Whether the bot is self-deaf.
        """
        return self.ws.update_voice_state(str(int(guild)), str(int(channel)) if channel else None, self_mute, self_deaf)

    @property
    def has_cache(self):
        return self.__use_cache

    @property
    def websocket_closed(self):
        """
        Whether the bot is disconnected from the Discord websocket.
        :return: bool
        """
        if self.ws:
            return self.ws.closed
        return True

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
        """
        try:
            self.loop.run_until_complete(self.start(reconnect_on_unknown_disconnect, compress))
        except KeyboardInterrupt:
            print("Detected KeyboardInterrupt, exiting...", file=sys.stderr)
        except Exception as ex:
            print("Unexpected exception occurred, exiting...", file=sys.stderr)
            traceback.print_exc()
        finally:
            self.loop.run_until_complete(self.close())
