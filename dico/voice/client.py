import time
import asyncio
import logging

from typing import TYPE_CHECKING, Optional

from .opus import DELAY_SECONDS
from .websocket import VoiceWebsocket

if TYPE_CHECKING:
    from .audio import AudioBase
    from ..client import Client
    from ..model import VoiceServerUpdate, VoiceState


class VoiceClient:
    """
    Client dedicated for voice control.

    .. warning::
       You should create this instance using :meth:`~.Client.connect_voice`.

    :param Client client: Client of your bot.
    :param VoiceWebsocket ws: Voice Websocket instance.

    :param Client ~.client: Client of your bot.
    :param VoiceWebsocket ~.ws: Voice Websocket instance.
    """

    def __init__(self, client: "Client", ws: VoiceWebsocket):
        self.client: "Client" = client
        self.ws: VoiceWebsocket = ws
        self.logger: logging.Logger = logging.getLogger(f"dico.voice.{ws.guild_id}")
        self.__audio_loaded = False
        self.__playing = False
        self.__not_paused = asyncio.Event()
        self.__not_paused.set()
        self.__audio_done = asyncio.Future()
        self.__audio = None
        self.__audio_task = None

    def __del__(self):
        if (
            self.__audio_task
            and not self.__audio_task.cancelled()
            and not self.__audio_task.done()
        ):
            self.__audio_task.cancel()

    async def close(self):
        """
        Closes and terminates voice instance.
        """
        if self.playing:
            await self.stop()
        await self.ws.close()
        await self.client.update_voice_state(self.ws.guild_id)

    def voice_state_update(self, payload: "VoiceState"):
        """
        Updates websocket session ID using received voice state payload.

        .. note::
            This is automatically handled inside the client.

        :param VoiceState payload: Voice state payload received.
        """
        self.ws.session_id = payload.session_id

    def voice_server_update(self, payload: "VoiceServerUpdate"):
        """
        Sets new voice server using voice server update payload.

        .. note::
            This is automatically handled inside the client.

        :param VoiceServerUpdate payload: Voice server update payload received.
        """
        self.ws.set_reconnect_voice_server(payload)

    async def play(self, audio: "AudioBase", *, lock_audio: bool = False):
        """
        Plays audio.

        :param AudioBase audio: Audio to play.
        :param bool lock_audio: Whether to lock audio. This is useful if your audio is dynamically updated.
        """
        await self.ws.speaking()
        if self.__audio_loaded:
            task = self.__audio_task
            if not task.done():
                await task
        self.__playing = True
        self.logger.debug("Loaded new audio.")
        self.__audio_task = self.client.loop.create_task(
            self.__play(audio, lock_audio=lock_audio)
        )

    async def __play(self, audio: "AudioBase", *, lock_audio: bool = False):
        start = time.perf_counter()
        count = 0
        if self.__audio_loaded:
            raise RuntimeError("Audio already loaded")
        self.__audio_loaded = True
        self.__audio_done = asyncio.Future()
        self.__audio = audio
        while self.__playing:
            if self.ws.destroyed:
                self.logger.warning("Voice websocket destroyed, closing voice client.")
                self.__playing = False
                if not self.__audio_done.done():
                    self.__audio_done.set_result(True)
                await self.close()
                break
            if not self.__not_paused.is_set():
                await self.ws.speaking(is_speaking=False)
                await self.__not_paused.wait()
                await self.ws.speaking()
                start = time.perf_counter()
                count = 0
            if not self.ws.ready:
                await self.ws.wait_ready()
                await self.ws.speaking()
                start = time.perf_counter()
                count = 0
            data = audio.read()
            if not data and not lock_audio:
                break
            elif not data and lock_audio:
                self.ws.sock.send(b"\xF8\xFF\xFE", encode_opus=False)
            else:
                self.ws.sock.send(data, encode_opus=not audio.is_opus())
            count += 1
            next_at = start + (DELAY_SECONDS * count)
            await asyncio.sleep(max(0, next_at - time.perf_counter()))
        if not self.ws.closed:
            await self.stop()
        self.__audio_loaded = False
        self.__audio = None

    def pause(self):
        """
        Pauses player.
        """
        self.__not_paused.clear()

    def resume(self):
        """
        Resumes paused player.
        """
        self.__not_paused.set()

    async def stop(self):
        """
        Stops player.
        """
        self.__playing = False
        if not self.__audio_done.done():
            self.__audio_done.set_result(True)
        await self.ws.speaking(is_speaking=False)

    async def wait_audio_done(self):
        """
        Waits until current audio is done playing.

        .. note::
            This will never done if audio is locked.
        """
        if not self.__audio_done.done():
            await self.__audio_done

    @property
    def playing(self) -> bool:
        """
        Whether audio is loaded.
        """
        return self.__playing

    @property
    def paused(self) -> bool:
        """
        Whether player is paused.
        """
        return not self.__not_paused.is_set()

    @property
    def audio(self) -> Optional["AudioBase"]:
        """
        Current audio playing.
        """
        return self.__audio

    @classmethod
    async def connect(
        cls,
        client: "Client",
        payload: "VoiceServerUpdate",
        voice_state: "VoiceState",
        wait_ready: bool = True,
    ) -> "VoiceClient":
        """
        Connects to the voice.

        .. warning::
           You should connect using :meth:`~.Client.connect_voice`.

        :param Client client: Client of your bot.
        :param VoiceServerUpdate payload: Voice server update payload received.
        :param VoiceState voice_state: Voice state payload received.
        :param bool wait_ready: Whether to wait until websocket is ready.
        :return: :class:`~.VoiceClient`
        """
        ws = await VoiceWebsocket.connect(client, payload, voice_state)
        client.loop.create_task(ws.run())
        if wait_ready:
            await ws.wait_ready()
        return cls(client, ws)
