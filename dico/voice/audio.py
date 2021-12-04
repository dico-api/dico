"""
AudioBase is from discord.py's AudioSource.
https://github.com/Rapptz/discord.py/blob/master/discord/player.py#L71
LICENSE(MIT): https://github.com/Rapptz/discord.py/blob/master/LICENSE
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .client import VoiceClient
    from ..model import FILE_TYPE


class AudioBase(ABC):
    def __del__(self):
        self.cleanup()

    @abstractmethod
    def read(self):
        pass

    @staticmethod
    def is_opus() -> bool:
        return False

    def cleanup(self):
        pass


"""
class FileAudio(AudioBase):
    def __init__(self, file: FILE_TYPE):
        self.file = file if not isinstance(file, str) else open(file, "rb")

    def __del__(self):
        if not self.file.closed:
            self.file.close()
"""


class Player:
    def __init__(self, parent: "VoiceClient", audio: AudioBase):
        self.parent = parent
        self.audio = audio

    def start(self):
        self.parent.ws.sock.send()
