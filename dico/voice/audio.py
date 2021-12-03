from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..model import FILE_TYPE


class AudioBase(ABC):
    pass


class FileAudio(AudioBase):
    def __init__(self, file: FILE_TYPE):
        self.file = file if not isinstance(file, str) else open(file, "rb")

    def __del__(self):
        if not self.file.closed:
            self.file.close()


class Player:
    def __init__(self, audio):
        self.audio = audio
