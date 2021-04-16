import inspect
from .model.event import *


class EventHandler:
    def __init__(self, dispatch):
        self.events = {}
        self.dispatch = dispatch

    def add(self, event, func):
        if event not in self.events:
            self.events[event] = []

        async def ensure_coro(*args, **kwargs):
            if inspect.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            else:
                return func(*args, **kwargs)

        self.events[event].append(ensure_coro)

    def get(self, event) -> list:
        return self.events.get(event, [])

    def dispatch_from_raw(self, name, resp):
        model_dict = {
            "READY": Ready,
            "MESSAGE_CREATE": MessageCreate,
            "CHANNEL_CREATE": ChannelCreate,
            "CHANNEL_UPDATE": ChannelUpdate,
            "CHANNEL_DELETE": ChannelDelete
        }
        if name in model_dict:
            ret = model_dict[name].create(resp)
        else:
            ret = resp
        self.dispatch(name, ret)
