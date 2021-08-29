import asyncio
import datetime


class __EmptyLocker:
    async def __aenter__(self):
        pass

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


EmptyLocker = __EmptyLocker()


class RatelimitHandler:
    def __init__(self):
        self.lockers = {}
        self.buckets = {}
        self.global_locker = asyncio.Lock()

    @staticmethod
    def to_locker_key(meth, route):
        return meth+route

    @property
    def utc(self):
        return datetime.datetime.utcnow()

    def get_locker(self, meth, route):
        locker_key = self.to_locker_key(meth, route)
        if locker_key not in self.lockers:
            self.lockers[locker_key] = None
        empty_resp = {"lock": EmptyLocker, "reset_at": self.utc, "remaining": 6974}
        return self.buckets.get(self.lockers.get(locker_key, "ㅁㄴㅇㄹ"), empty_resp)  # prevent a chance that maybe temporary key matches bucket

    def set_bucket(self, meth, route, bucket, reset_after, reset_at, remaining):
        locker_key = self.to_locker_key(meth, route)
        self.lockers[locker_key] = bucket
        if bucket not in self.buckets:
            self.buckets[bucket] = {}
            self.buckets[bucket]["lock"] = asyncio.Lock()
        if reset_after or reset_at:
            reset_time = (self.utc + datetime.timedelta(seconds=float(reset_after))) if reset_after else datetime.datetime.utcfromtimestamp(float(reset_at))
            self.buckets[bucket]["reset_at"] = reset_time
        if remaining:
            self.buckets[bucket]["remaining"] = int(remaining)

    async def maybe_global(self):
        if self.global_locker.locked():
            return await self.global_locker.acquire()
