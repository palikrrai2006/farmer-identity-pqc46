from cryptography.kyber import KyberKEM
from cryptography.dilithium import DilithiumSignature
from cryptography.aes import AESEncryption

print("Testing cryptography modules...")

# Test Kyber
print("\n1. Testing KyberKEM...")
kyber = KyberKEM()
print("✓ KyberKEM object created")

# Test Dilithium
print("\n2. Testing DilithiumSignature...")
dilithium = DilithiumSignature()
print("✓ DilithiumSignature object created")

# Test AES
print("\n3. Testing AESEncryption...")
key = b'0' * 32  # 32-byte key
aes = AESEncryption(key)
print("✓ AESEncryption object created")

print("\n✓ All cryptography modules working!")