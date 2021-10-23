import io
import base64
import pathlib
from typing import Union, Awaitable, Text

try:
    from typing import Literal

    WidgetStyle = Literal["shield", "banner1", "banner2", "banner3", "banner4"]
except ImportError:
    WidgetStyle = Text


class File:
    def __init__(self, raw: bytes, name: str = "unknown", extension: str = "png"):
        self.raw: bytes = raw
        self.filename: str = name
        self.extension: str = extension

    def read(self):
        return self.raw

    def to_image_data(self):
        img = base64.b64encode(self.raw)
        return f"data:image/{self.extension};base64,{img.decode()}"

    @property
    def name(self):
        return f"{self.filename}.{self.extension}"


FILE_TYPE = Union[io.FileIO, pathlib.Path, str, File]
BYTES_RESPONSE = Union[bytes, Awaitable[bytes]]
