from dilithium_py.dilithium import Dilithium5

class DilithiumSignature:
    def __init__(self):
        self.variant = "Dilithium5"

    def generate_keypair(self) -> dict:
        public_key, secret_key = Dilithium5.keygen()
        return {"public_key": public_key, "secret_key": secret_key}

    def sign(self, message: bytes, secret_key: bytes) -> bytes:
        return Dilithium5.sign(secret_key, message)

    def verify(self, message: bytes, signature: bytes, public_key: bytes) -> bool:
        try:
            Dilithium5.verify(public_key, message, signature)
            return True
        except Exception:
            return False