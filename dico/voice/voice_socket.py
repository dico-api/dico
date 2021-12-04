import struct
import socket
import asyncio

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .websocket import VoiceWebsocket


class VoiceSocket:
    def __init__(self, parent: "VoiceWebsocket", sock):
        self.sock: socket.socket = sock
        self.parent = parent
        self.seq = 0
        self.timestamp = 0
    
    @classmethod
    async def connect(cls, parent: "VoiceWebsocket", ip_discovery: bool = True):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setblocking(False)
        print("ip discovery?", ip_discovery)
        if ip_discovery:
            packet = bytearray(70)
            packet[0] = 0x1
            packet[2] = 70
            struct.pack_into(">I", packet, 4, parent.ssrc)
            print("sending...")
            sock.sendto(packet, (parent.ip, parent.port))
            print("sent, waiting...")
            resp = await parent.loop.sock_recv(sock, 70)
            print("resp is:", resp)
            self_ip = resp[4:resp.index(0, 4)].decode("ascii")
            self_port = struct.unpack_from(">H", resp, len(resp) - 2)[0]
            print(self_ip, self_port)
            parent.set_self_ip(self_ip, self_port)
        return cls(parent, sock)

    def generate_packet(self, data: bytes):
        header = bytearray(24)
        header[0] = 0x80
        header[1] = 0x78
        struct.pack_into(">H", header, 2, self.seq)  # 2 3
        struct.pack_into(">I", header, 4, self.timestamp)  # 4 5 6 7
        struct.pack_into(">I", header, 8, self.parent.ssrc)  # 8 9 10 11
        return self.parent.encryptor.get_encryptor(self.parent.mode)(header, data)

    def send(self, data: bytes):
        self.seq += 1
        self.timestamp += 0  # TODO: set to correct value
        packet = self.generate_packet(data)
        self.sock.sendto(packet, (self.parent.ip, self.parent.port))

    def close(self):
        self.sock.close()

    def reset(self):
        self.seq = 0
        self.timestamp = 0
