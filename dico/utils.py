import sys
import typing
import inspect
import traceback


async def safe_call(coro, additional_message: typing.Optional[str] = None):
    """
    Calls coroutine, ignoring raised exception and only print traceback.
    This is used for event listener call, and intended to be used at creating task.

    :param coro: Coroutine to safely call
    :param additional_message: Additional traceback message to print at the top.
    """

    try:
        await coro
    except Exception as ex:
        tb = traceback.format_exc()
        if additional_message:
            _p = additional_message+"\n"+tb
        else:
            _p = tb
        print(_p, file=sys.stderr)


def cdn_url(route, *, image_hash, extension="webp", size=1024, **snowflake_ids):
    if not 16 <= size <= 4096:
        raise ValueError("size must be between 16 and 4096.")
    if snowflake_ids:
        route = route.format(**snowflake_ids)
    return f"https://cdn.discordapp.com/{route}/{image_hash}.{extension}?size={size}"


def ensure_coro(func):
    async def wrap(*args, **kwargs):
        if inspect.iscoroutinefunction(func):
            return await func(*args, **kwargs)
        else:
            return func(*args, **kwargs)
    return wrap
