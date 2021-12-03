import ctypes


c_int_ptr = ctypes.POINTER(ctypes.c_int)
c_int16_ptr = ctypes.POINTER(ctypes.c_int16)
c_float_ptr = ctypes.POINTER(ctypes.c_float)

libopus = None

SAMPLE_RATE = 48000  # 48kbps
OPUS_APPLICATION_AUDIO = 2049


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

    def encode(self, pcm, frame_size, max_data_bytes):
        pcm = ctypes.cast(pcm, c_int16_ptr)
        return libopus.opus_encode(self.encoder, pcm, frame_size, max_data_bytes)
