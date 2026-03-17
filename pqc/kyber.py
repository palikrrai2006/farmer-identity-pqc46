from kyber_py.kyber import Kyber1024

class KyberKEM:
    def __init__(self):
        self.variant = "Kyber1024"

    def generate_keypair(self) -> dict:
        # ek = encapsulation key (public)
        # dk = decapsulation key (secret)
        ek, dk = Kyber1024.keygen()
        return {"public_key": ek, "secret_key": dk}

    def encapsulate(self, public_key: bytes) -> dict:
        # encaps returns (shared_secret, ciphertext) in v1.2.0
        shared_secret, ciphertext = Kyber1024.encaps(public_key)
        return {"ciphertext": ciphertext, "shared_secret": shared_secret}

    def decapsulate(self, secret_key: bytes, ciphertext: bytes) -> bytes:
        # decaps returns shared_secret
        shared_secret = Kyber1024.decaps(secret_key, ciphertext)
        return shared_secret