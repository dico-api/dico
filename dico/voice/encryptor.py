from nacl import secret
from nacl import utils


class Encryptor:
    AVAILABLE = ["xsalsa20_poly1305_suffix"]

    def __init__(self, secret_key):
        self.secret_key = bytes(secret_key)
        self.box = secret.SecretBox(self.secret_key)

    def get_encryptor(self, mode: str):
        if mode not in self.AVAILABLE:
            raise ValueError("Encoder mode not available")
        return getattr(self, mode)

    def xsalsa20_poly1305_suffix(self, header: bytearray, data: bytes):
        nonce = utils.random(secret.SecretBox.NONCE_SIZE)
        return header + self.box.encrypt(data, nonce).ciphertext + nonce
