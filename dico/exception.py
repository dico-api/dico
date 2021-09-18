import typing

from .utils import format_discord_error


class DicoException(Exception):
    """Base exception class for this library."""


class WebsocketClosed(DicoException):
    """Websocket is closed, so this action could not be performed."""


class WebsocketRateLimited(DicoException):
    """Websocket is rate limit, try again later."""
    def __init__(self, left: float):
        self.left: float = left
        super().__init__(f"Please try again after {self.left} seconds.")


class DownloadFailed(DicoException):
    """Downloading something has failed."""
    def __init__(self, url: str, code: int, resp: typing.Any):
        self.url: str = url
        self.code: int = code
        self.resp: typing.Any = resp
        super().__init__(f"Download failed with {self.code}: {self.url}")


class HTTPError(DicoException):
    """Special exception class for HTTP."""
    def __init__(self, route: str, code: int, resp: typing.Any):
        self.route: str = route
        self.code: int = code
        self.resp: typing.Any = resp
        super().__init__(format_discord_error(self.resp))


class DiscordError(HTTPError):
    """Discord has an error."""


class BadRequest(HTTPError):
    """We sent incorrect request."""


class Forbidden(HTTPError):
    """We don't have permission for this request."""


class NotFound(HTTPError):
    """This request isn't something available."""


class RateLimited(HTTPError):
    """We are rate-limited and couldn't successfully requesting in desired count."""


class Unknown(HTTPError):
    """Failed handling this type of error. If you see this report to GitHub Issues."""
