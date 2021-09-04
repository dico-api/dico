import time
import asyncio

from ..exception import WebsocketRateLimited


class WSRatelimit:
    def __init__(self, heartbeat_time=6):
        self.count = 0
        self.init_time = time.time()
        self.locker = asyncio.Lock()
        self.max_requests = int(120 - (60 / heartbeat_time))

    def maybe_limited(self):
        now = time.time()
        if self.init_time + 60 >= now and self.count >= self.max_requests:
            raise WebsocketRateLimited((self.init_time + 60) - now)
        elif self.init_time + 60 <= now:
            self.init_time = now
            self.count = 0
        self.count += 1
        return self.locker

    def reload_heartbeat(self, heartbeat_time):
        self.max_requests = int(120 - (60 / heartbeat_time))
