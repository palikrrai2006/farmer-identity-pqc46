import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import hashlib

class AESEncryption:
    def __init__(self, key: bytes = None):
        """key must be 32 bytes for AES-256. If not provided, generates one."""
        self.key = key if key else os.urandom(32)

    def encrypt(self, plaintext: bytes) -> dict:
        """Encrypts plaintext. Returns ciphertext + nonce."""
        nonce = os.urandom(12)
        aesgcm = AESGCM(self.key)
        ciphertext = aesgcm.encrypt(nonce, plaintext, None)
        return {
            "ciphertext": ciphertext,
            "nonce": nonce,
            "key": self.key
        }

    def decrypt(self, ciphertext: bytes, nonce: bytes) -> bytes:
        """Decrypts ciphertext using nonce."""
        aesgcm = AESGCM(self.key)
        return aesgcm.decrypt(nonce, ciphertext, None)

    @staticmethod
    def hash_sha3_256(data: bytes) -> str:
        """Returns SHA3-256 hash as hex string."""
        return hashlib.sha3_256(data).hexdigest()