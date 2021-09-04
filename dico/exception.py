from .utils import format_discord_error


class DicoException(Exception):
    """Base exception class for this library."""


class WebsocketClosed(DicoException):
    """Websocket is closed, so this action could not be performed."""


class WebsocketRateLimited(DicoException):
    """Websocket is rate limit, try again later."""
    def __init__(self, left):
        self.left = left
        super().__init__(f"Please try again after {self.left} seconds.")


class DownloadFailed(DicoException):
    """Downloading something has failed."""
    def __init__(self, url, code, resp):
        self.url = url
        self.code = code
        self.resp = resp
        super().__init__(f"Download failed with {self.code}: {self.url}")


class HTTPError(DicoException):
    """Special exception class for HTTP."""
    def __init__(self, route, code, resp):
        self.route = route
        self.code = code
        self.resp = resp
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
