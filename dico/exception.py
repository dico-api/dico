class DicoException(Exception):
    """Base exception class for this library."""


class HTTPError(DicoException):
    """Special exception class for HTTP."""
    def __init__(self, route, code, resp):
        self.route = route
        self.code = code
        self.resp = resp


class DiscordError(HTTPError):
    """Discord has an error."""


class RateLimited(HTTPError):
    """We are rate-limited and couldn't successfully requesting in desired count."""


class Unknown(HTTPError):
    """Failed handling this type of error. If you see this report to GitHub Issues."""
