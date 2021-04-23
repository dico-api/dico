import typing
import asyncio
import traceback
from . import utils
from .base.http import HTTPRequestBase
from .http.async_http import AsyncHTTPRequest
from .ws.websocket import WebSocketClient
from .cache import ClientCacheContainer
from .handler import EventHandler
from .model import Intents


class APIClient:
    def __init__(self, token, *, base: HTTPRequestBase, **http_options):
        self.http = base.create(token, **http_options)

    def send_message(self):
        pass


class Client:
    def __init__(self, token: str, *, intents=Intents.no_privileged(), loop=None):
        self.loop = loop or asyncio.get_event_loop()
        self.token = token
        self.http = AsyncHTTPRequest(self.token, loop)
        self.cache = ClientCacheContainer()
        self.__ws_class = WebSocketClient
        self.intents = intents
        self.ws: typing.Union[None, WebSocketClient] = None
        self.events = EventHandler(self.dispatch)

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

    def run(self):
        self.loop.run_until_complete(self.start())
