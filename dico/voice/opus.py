"""
This code is referred from kijk2869/discodo: https://github.com/kijk2869/discodo/blob/2693c6cb678584036658693f305feb6df5f743b0/discodo/natives/opus.py.
LICENSE(MIT): https://github.com/kijk2869/discodo/blob/master/LICENSE
"""

import array
import ctypes


c_int_ptr = ctypes.POINTER(ctypes.c_int)
c_int16_ptr = ctypes.POINTER(ctypes.c_int16)
c_float_ptr = ctypes.POINTER(ctypes.c_float)

libopus = None
OPUS_APPLICATION_AUDIO = 2049
CTL_SET_BITRATE = 4002
CTL_SET_FEC = 4003
CTL_SET_PLP = 4014
CTL_SET_BANDWIDTH = 4008
CTL_SET_SIGNAL = 4024
BAND_CTL_FULL = 1105
SIGNAL_CTL_MUSIC = 3002

SAMPLE_RATE = 48000  # 48kbps
FRAME_LENGTH = 20  # 20ms
SAMPLES_PER_FRAME = int(SAMPLE_RATE / 1000 * FRAME_LENGTH)
FRAME_SIZE = SAMPLES_PER_FRAME ** 2
DELAY_SECONDS = FRAME_LENGTH / 1000
BITRATE = 128
EXPECTED_PACKETLOSS = 0  # ...maybe?


def load_libopus(name: str = "libopus-0.x64.dll"):
    global libopus
    libopus = ctypes.cdll.LoadLibrary(name)
    return libopus


class OpusEncoder:
    def __init__(self):
        if not libopus:
            load_libopus()
        ret = ctypes.c_int()
        self.encoder = libopus.opus_encoder_create(SAMPLE_RATE, 2, OPUS_APPLICATION_AUDIO, ctypes.byref(ret))
        self.set_bitrate()
        self.set_fec()
        self.set_expected_pack_loss()
        self.set_bandwidth()
        self.set_signal_type()

    def __del__(self):
        if self.encoder:
            libopus.opus_encoder_destroy(self.encoder)
            self.encoder = None

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
        resp = libopus.opus_encode(self.encoder, pcm, FRAME_SIZE, data, max_data_bytes)
        return array.array("b", data[:resp]).tobytes()
