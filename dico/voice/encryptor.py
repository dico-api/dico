try:
    from nacl import secret
    from nacl import utils
except ImportError:
    import sys

    print("PyNaCl not found, voice won't be available.", file=sys.stderr)
    secret = None
    utils = None


class Encryptor:
    AVAILABLE = ["xsalsa20_poly1305_suffix"] if secret and utils else []

    def __init__(self, secret_key):
        if secret and utils:
            self.secret_key = bytes(secret_key)
            self.box = secret.SecretBox(self.secret_key)

    def get_encryptor(self, mode: str):
        if mode not in self.AVAILABLE:
            raise ValueError("Encryptor mode not available")
        return getattr(self, mode)

    def xsalsa20_poly1305_suffix(self, header: bytearray, data: bytes):
        nonce = utils.random(secret.SecretBox.NONCE_SIZE)
        return header + self.box.encrypt(data, nonce).ciphertext + nonce
