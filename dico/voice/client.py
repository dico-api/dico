import time
import asyncio
import logging

from typing import TYPE_CHECKING

from .opus import DELAY_SECONDS
from .websocket import VoiceWebsocket

if TYPE_CHECKING:
    from .audio import AudioBase
    from ..client import Client
    from ..model import VoiceServerUpdate, VoiceState


class VoiceClient:
    def __init__(self, client: "Client", ws: VoiceWebsocket):
        self.client = client
        self.ws = ws
        self.logger = logging.getLogger(f"dico.voice.{ws.guild_id}")
        self.__audio_loaded = False
        self.__playing = False
        self.__not_paused = asyncio.Event()
        self.__not_paused.set()
        self.__audio_done = asyncio.Future()

    async def close(self):
        if self.playing:
            await self.stop()
        await self.ws.close()

    async def __voice_state_update(self, payload: "VoiceState"):
        self.ws.session_id = payload.session_id

    async def __voice_server_update(self, payload: "VoiceServerUpdate"):
        pass

    async def play(self, audio: "AudioBase"):
        await self.ws.speaking()
        self.__playing = True
        if not self.__audio_loaded:
            self.logger.debug("Loaded new audio.")
            self.client.loop.create_task(self.__play(audio))

    async def __play(self, audio: "AudioBase"):
        start = time.perf_counter()
        count = 0
        if self.__audio_loaded:
            raise RuntimeError("Audio already loaded")
        self.__audio_loaded = True
        self.__audio_done = asyncio.Future()
        while self.__playing:
            if not self.__not_paused.is_set():
                await self.__not_paused.wait()
            data = audio.read()
            if not data:
                break
            self.ws.sock.send(data, encode_opus=not audio.is_opus())
            count += 1
            next_at = start + (DELAY_SECONDS * count)
            await asyncio.sleep(max(0, next_at - time.perf_counter()))
        await self.stop()
        self.__audio_loaded = False

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
    def playing(self):
        return self.__playing

    @property
    def paused(self):
        return not self.__not_paused.is_set()

    @classmethod
    async def connect(cls, client: "Client", payload: "VoiceServerUpdate", voice_state: "VoiceState", wait_ready: bool = True):
        ws = await VoiceWebsocket.connect(client, payload, voice_state)
        client.loop.create_task(ws.run())
        if wait_ready:
            await ws.wait_ready()
        return cls(client, ws)
