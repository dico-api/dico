import struct
import socket
import asyncio

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .websocket import VoiceWebsocket


class VoiceSocket:
    def __init__(self, parent: "VoiceWebsocket", sock):
        self.sock = sock
        self.parent = parent
        self.seq = None
        self.timestamp = None
    
    @classmethod
    async def connect(cls, parent: "VoiceWebsocket", ip_discovery: bool = False):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setblocking(False)
        if ip_discovery:
            packet = bytearray(74)
            packet[0] = 0x1
            packet[2] = 70
            struct.pack_into(">I", packet, 4, self.parent.ssrc)
            sock.sendto(packet, (self.parent.ip, self.parent.port))
            resp = await self.parent.loop.sock_recv(sock)
        return cls(parent, sock)

    def generate_packet(self, data: bytes):
        header = bytearray(24)
        header[0] = 0x80
        header[1] = 0x78
        struct.pack_into(">H", header, 2, self.seq)  # 2 3
        struct.pack_into(">I", header, 4, self.timestamp)  # 4 5 6 7
        struct.pack_into(">I", header, 8, self.parent.ssrc)  # 8 9 10 11
        return self.parent.encoder.get_encoder(self.parent.mode)(header, data)
