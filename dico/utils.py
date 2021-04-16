import sys
import typing
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
