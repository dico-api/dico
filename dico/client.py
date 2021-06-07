import sys
import typing
import asyncio
import traceback
from . import utils
from .api import APIClient
from .http.async_http import AsyncHTTPRequest
from .ws.websocket import WebSocketClient
from .cache import CacheContainer
from .handler import EventHandler
from .model import Intents, AllowedMentions, Snowflake, Application, Activity


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
    :ivar application_id: ID of the application. Can be ``None`` if Ready event is not called, and if it is, you must pass parameter application_id for all methods that has it.
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
        self.__wait_futures = {}
        self.application_id = None

        # Custom events dispatch
        self.events.add("READY", self.__ready)
        self.events.add("VOICE_STATE_UPDATE", self.__voice_state_update)
        # self.events.add("MESSAGE_CREATE", lambda x: self.events.dispatch("MESSAGE", x.message))

    def __ready(self, ready):
        self.application_id = Snowflake(ready.application["id"])

    def __voice_state_update(self, voice_state):
        if self.has_cache:
            user = self.get(voice_state.user_id)
            if user:
                user.set_voice_state(voice_state)

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
        return wrap if meth is None else wrap()

    @property
    def on(self):
        return self.on_

    async def wait(self, event_name: str, timeout: float = None, check: typing.Callable = None):
        async def wrap():
            while True:
                future = asyncio.Future()
                if event_name.upper() not in self.__wait_futures:
                    self.__wait_futures[event_name.upper()] = []
                self.__wait_futures[event_name.upper()].append(future)
                res = await asyncio.wait_for(future, timeout=None, loop=self.loop)
                ret = res if len(res) > 1 else res[0]
                if check and check(*res):
                    return ret
                elif not check:
                    return ret
        return await asyncio.wait_for(wrap(), timeout=timeout, loop=self.loop)

    def dispatch(self, name, *args):
        """
        Dispatches new event.

        :param name: Name of the event.
        :param args: Arguments of the event.
        """
        [self.loop.create_task(utils.safe_call(x(*args))) for x in self.events.get(name.upper())]
        [self.__wait_futures[name.upper()].pop(x).set_result(args) for x in range(len(self.__wait_futures.get(name.upper(), [])))]

    @property
    def get(self):
        """Alias of ``.cache.get``."""
        if self.has_cache:
            return self.cache.get

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

    @property
    def has_cache(self):
        return self.__use_cache

    def __setattr__(self, key, value):
        if not key.lower().startswith("on_") or key.lower() in ["on", "on_"]:
            return super().__setattr__(key, value)
        event_name = key.lower().lstrip("on_")
        return self.on_(event_name, value)

    def __getattr__(self, item):
        if not item.lower().startswith("on_") or item.lower() in ["on", "on_"]:
            return super().__getattribute__(item)  # Should raise AttributeError or whatever.
        event_name = item.lower().lstrip("on_")

        def deco(func):
            return self.on_(event_name, func)

        return deco

    def run(self):
        """
        Runs client. Actually this is sync function wrapping :meth:`.start`.

        .. warning::
            This must be placed at the end of the code.
        """
        self.loop.run_until_complete(self.start())
