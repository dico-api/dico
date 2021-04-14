from .model.event import *


class EventHandler:
    def __init__(self, dispatch):
        self.events = {}
        self.dispatch = dispatch

    def add(self, event, coro):
        if event not in self.events:
            self.events[event] = []
        self.events[event].append(coro)

    def get(self, event) -> list:
        return self.events.get(event, [])

    def dispatch_from_raw(self, name, resp):
        model_dict = {
            "READY": Ready,
            "MESSAGE_CREATE": MessageCreate
        }
        if name in model_dict:
            ret = model_dict[name].create(resp)
        else:
            ret = resp
        self.dispatch(name, ret)
