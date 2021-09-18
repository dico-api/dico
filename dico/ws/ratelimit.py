import time
import asyncio

from ..exception import WebsocketRateLimited


class WSRatelimit:
    def __init__(self, heartbeat_time: int = 6):
        self.count: int = 0
        self.init_time: float = time.time()
        self.locker: asyncio.Lock = asyncio.Lock()
        self.max_requests: int = int(120 - (60 / heartbeat_time))

    def maybe_limited(self) -> asyncio.Lock:
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

    def reset_after(self) -> float:
        return self.init_time + 60 - time.time()
