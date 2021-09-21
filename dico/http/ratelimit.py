import asyncio
import datetime
import typing


class __EmptyLocker:
    async def __aenter__(self):
        pass

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


EmptyLocker = __EmptyLocker()


class RatelimitHandler:
    """
    Rate limit handler for :class:`.async_http.AsyncHTTPRequest`.

    :ivar lockers: Dictionary of lockers per buckets.
    :ivar buckets: Dictionary of buckets to be used for the route.
    :ivar global_locker: Locker for global rate limit situation.
    """
    def __init__(self):
        self.lockers: typing.Dict[str, typing.Optional[str]] = {}
        self.buckets: typing.Dict[str, dict] = {}
        self.global_locker: asyncio.Lock = asyncio.Lock()

    @staticmethod
    def to_locker_key(meth: str, route: str):
        """Merges method and route."""
        return meth+route

    @property
    def utc(self):
        """Current time as UTC. Used for calculation of rate limit expiration time."""
        return datetime.datetime.utcnow()

    def get_locker(self, meth: str, route: str) -> dict:
        """
        Gets locker based on method and route passed.

        :param meth: Method of the request.
        :param route: Route of the request.
        :return: Format of: ``{"lock": LOCKER_INSTANCE, "reset_at": EXPIRATION_TIME, "remaining": REMAINING_COUNT}``
        """
        locker_key = self.to_locker_key(meth, route)
        if locker_key not in self.lockers:
            self.lockers[locker_key] = None
        empty_resp = {"lock": EmptyLocker, "reset_at": self.utc, "remaining": 6974}
        return self.buckets.get(self.lockers.get(locker_key, "ㅁㄴㅇㄹ"), empty_resp)  # prevent a chance that maybe temporary key matches bucket

    def set_bucket(self, meth: str, route: str, bucket: str, reset_after: typing.Union[str, int, float], reset_at: typing.Union[str, int, float], remaining: typing.Union[str, int]):
        """
        Creates bucket based on rate limit response headers.

        :param meth: Method of the request.
        :param route: Route of the request.
        :param bucket: Bucket of the request.
        :param reset_after: Second of the reset time left.
        :param reset_at: Timestamp of when the rate limit resets.
        :param remaining: Remaining request count.
        """
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
        """Waits until global lock expires."""
        if self.global_locker.locked():
            async with self.global_locker:
                return
