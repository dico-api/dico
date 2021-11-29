import struct
import asyncio

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .websocket import VoiceWebsocket


class VoiceSocket:
    def __init__(self, parent: "VoiceWebsocket"):
        self.parent = parent
        self.seq = None
        self.timestamp = None

    def generate_packet(self, data: bytes):
        header = bytearray(24)
        header[0] = 0x80
        header[1] = 0x78
        struct.pack_into(">H", header, 2, self.seq)  # 2 3
        struct.pack_into(">I", header, 4, self.timestamp)  # 4 5 6 7
        struct.pack_into(">I", header, 8, self.parent.ssrc)  # 8 9 10 11
        return self.parent.encoder.get_encoder(self.parent.mode)(header, data)
