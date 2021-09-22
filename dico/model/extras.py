import io
import pathlib
from typing import Union, Awaitable

FILE_TYPE = Union[io.FileIO, pathlib.Path, str]
BYTES_RESPONSE = Union[bytes, Awaitable[bytes]]
