"""
AudioBase structure is from discord.py's AudioSource.
https://github.com/Rapptz/discord.py/blob/master/discord/player.py#L71
LICENSE(MIT): https://github.com/Rapptz/discord.py/blob/master/LICENSE
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .client import VoiceClient
    from ..model import FILE_TYPE


class AudioBase(ABC):
    """
    Base structure of the audio.
    """
    def __del__(self):
        self.cleanup()

    @abstractmethod
    def read(self) -> bytes:
        """
        This should read 20ms of the audio.

        :return: bytes
        """
        pass

    @staticmethod
    def is_opus() -> bool:
        """
        Whether this is already opus.
        """
        return False

    def cleanup(self):
        """
        Optionally clean up before destroying this audio instance.
        """
        pass


"""
class FileAudio(AudioBase):
    def __init__(self, file: FILE_TYPE):
        self.file = file if not isinstance(file, str) else open(file, "rb")
    
    def read(self):
        pass

    def cleanup(self):
        if not self.file.closed:
            self.file.close()
"""
