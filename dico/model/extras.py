import io
import typing
import pathlib

FILE_TYPE = typing.Union[io.FileIO, pathlib.Path, str]
BYTES_RESPONSE = typing.Union[bytes, typing.Awaitable[bytes]]
