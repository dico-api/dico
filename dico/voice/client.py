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

    async def close(self):
        if self.playing:
            await self.stop()
        await self.ws.close()
        await self.client.update_voice_state(self.ws.guild_id)

    def voice_state_update(self, payload: "VoiceState"):
        self.ws.session_id = payload.session_id

    def voice_server_update(self, payload: "VoiceServerUpdate"):
        self.ws.set_reconnect_voice_server(payload)

    async def play(self, audio: "AudioBase", *, lock_audio: bool = False):
        await self.ws.speaking()
        self.__playing = True
        if not self.__audio_loaded:
            self.logger.debug("Loaded new audio.")
            self.client.loop.create_task(self.__play(audio, lock_audio=lock_audio))

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
        self.__not_paused.clear()

    def resume(self):
        self.__not_paused.set()

    async def stop(self):
        self.__playing = False
        if not self.__audio_done.done():
            self.__audio_done.set_result(True)
        await self.ws.speaking(is_speaking=False)

    async def wait_audio_done(self):
        if not self.__audio_done.done():
            await self.__audio_done

    @property
    def playing(self) -> bool:
        return self.__playing

    @property
    def paused(self) -> bool:
        return not self.__not_paused.is_set()

    @property
    def audio(self) -> Optional["AudioBase"]:
        return self.__audio

    @classmethod
    async def connect(cls, client: "Client", payload: "VoiceServerUpdate", voice_state: "VoiceState", wait_ready: bool = True):
        ws = await VoiceWebsocket.connect(client, payload, voice_state)
        client.loop.create_task(ws.run())
        if wait_ready:
            await ws.wait_ready()
        return cls(client, ws)
