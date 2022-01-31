"""
This code is referred from kijk2869/discodo: https://github.com/kijk2869/discodo/blob/2693c6cb678584036658693f305feb6df5f743b0/discodo/natives/opus.py.
LICENSE(MIT): https://github.com/kijk2869/discodo/blob/master/LICENSE
"""

import os
import sys
import array
import ctypes
import ctypes.util


c_int_ptr = ctypes.POINTER(ctypes.c_int)
c_int16_ptr = ctypes.POINTER(ctypes.c_int16)
c_float_ptr = ctypes.POINTER(ctypes.c_float)

libopus = None
OPUS_APPLICATION_AUDIO = 2049
CTL_SET_BITRATE = 4002
CTL_SET_FEC = 4012
CTL_SET_PLP = 4014
CTL_SET_BANDWIDTH = 4008
CTL_SET_SIGNAL = 4024
BAND_CTL_FULL = 1105
SIGNAL_CTL_MUSIC = 3002

SAMPLE_RATE = 48000  # 48kbps
FRAME_LENGTH = 20  # 20ms
SAMPLES_PER_FRAME = int(SAMPLE_RATE / 1000 * FRAME_LENGTH)
CHANNELS = 2
FRAME_SIZE = SAMPLES_PER_FRAME * CHANNELS * 2
DELAY_SECONDS = FRAME_LENGTH / 1000
BITRATE = 128
EXPECTED_PACKETLOSS = 0  # ...maybe?


def load_libopus(name: str = None):
    if not name:
        if sys.platform == "win32":
            architecture = "x64" if sys.maxsize > 32**2 else "x86"
            directory = os.path.dirname(os.path.abspath(__file__))
            name = os.path.join(directory, "bin", f"opus-{architecture}.dll")
        else:
            name = ctypes.util.find_library("opus")
    global libopus
    libopus = ctypes.cdll.LoadLibrary(name)
    libopus.opus_encoder_create.argtypes = [
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
        c_int_ptr,
    ]
    libopus.opus_encoder_create.restype = ctypes.c_void_p
    libopus.opus_encoder_ctl.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
    libopus.opus_encode.argtypes = [
        ctypes.c_void_p,
        c_int16_ptr,
        ctypes.c_int,
        ctypes.c_char_p,
        ctypes.c_int32,
    ]
    libopus.opus_encoder_destroy.argtypes = [ctypes.c_void_p]
    return libopus


class OpusEncoder:
    def __init__(self):
        if not libopus:
            load_libopus()
        self.encoder = self.create_encoder()
        self.set_bitrate()
        self.set_fec()
        self.set_expected_pack_loss()
        self.set_bandwidth()
        self.set_signal_type()

    def __del__(self):
        if self.encoder:
            libopus.opus_encoder_destroy(self.encoder)
            self.encoder = None

    def create_encoder(self):
        ret = ctypes.c_int()
        return libopus.opus_encoder_create(
            SAMPLE_RATE, 2, OPUS_APPLICATION_AUDIO, ctypes.byref(ret)
        )

    def set_bitrate(self):
        kbps = min(512, max(16, int(BITRATE)))
        libopus.opus_encoder_ctl(self.encoder, CTL_SET_BITRATE, kbps * 1024)

    def set_fec(self):
        libopus.opus_encoder_ctl(self.encoder, CTL_SET_FEC, 1)

    def set_expected_pack_loss(self):
        libopus.opus_encoder_ctl(self.encoder, CTL_SET_PLP, EXPECTED_PACKETLOSS)

    def set_bandwidth(self):
        libopus.opus_encoder_ctl(self.encoder, CTL_SET_BANDWIDTH, BAND_CTL_FULL)

    def set_signal_type(self):
        libopus.opus_encoder_ctl(self.encoder, CTL_SET_SIGNAL, SIGNAL_CTL_MUSIC)

    def encode(self, pcm: bytes):
        max_data_bytes = len(pcm)
        pcm = ctypes.cast(pcm, c_int16_ptr)
        data = (ctypes.c_char * max_data_bytes)()
        resp = libopus.opus_encode(
            self.encoder, pcm, SAMPLES_PER_FRAME, data, max_data_bytes
        )
        return array.array("b", data[:resp]).tobytes()
