"""
AudioBase structure is from discord.py's AudioSource.
https://github.com/Rapptz/discord.py/blob/master/discord/player.py#L71
LICENSE(MIT): https://github.com/Rapptz/discord.py/blob/master/LICENSE
"""

import audioop
import subprocess

from abc import ABC, abstractmethod
from typing import Union
from pathlib import Path

from .opus import FRAME_SIZE


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


class Audio(AudioBase):
    """
    Audio for playing from file or URL.

    :param src: Source of the audio.
    :type src: Union[str, Path]

    :ivar subprocess.Popen ~.process: FFmpeg process for processing source.
    :ivar float ~.volume: Volume of the audio.
    """

    def __init__(self, src: Union[str, Path]):
        cmd = f"ffmpeg -i {src} -f s16le -ar 48000 -ac 2 -loglevel warning pipe:1"
        self.process: subprocess.Popen = subprocess.Popen(
            cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        self.volume: float = 1.0

    def read(self) -> bytes:
        """
        Reads 20ms of audio from source.

        :return: bytes
        """
        data = self.process.stdout.read(FRAME_SIZE)
        if len(data) != FRAME_SIZE:
            data = b""
        return audioop.mul(data, 2, min(max(self.volume, 0), 2.0))

    def cleanup(self):
        """
        Cleans up subprocess.
        """
        if self.process:
            self.process.kill()
