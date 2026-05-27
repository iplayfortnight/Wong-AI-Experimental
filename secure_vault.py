import os
import gc
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

SECTOR_SIZE = 4048
SALT_PATH = "vault_salt.bin"

class SecureDiskVault:
    def __init__(self, master_password: str):
        if not os.path.exists(SALT_PATH):
            self.salt = os.urandom(16)
            with open(SALT_PATH, "wb") as f:
                f.write(self.salt)
        else:
            with open(SALT_PATH, "rb") as f:
                self.salt = f.read()

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000
        )
        self.key = kdf.derive(master_password.encode())
        self.aesgcm = AESGCM(self.key)
        gc.collect()

    def encrypt_sector_block(self, plaintext_data: str) -> bytes:
        nonce = os.urandom(12)
        plaintext_bytes = plaintext_data.encode('utf-8').ljust(SECTOR_SIZE - 28, b'\x00')
        ciphertext = self.aesgcm.encrypt(nonce, plaintext_bytes, None)
        return nonce + ciphertext

    def decrypt_sector_block(self, raw_bytes: bytes) -> str:
        if len(raw_bytes) < 28:
            return ""
        nonce = raw_bytes[:12]
        ciphertext = raw_bytes[12:]
        try:
            plaintext_bytes = self.aesgcm.decrypt(nonce, ciphertext, None)
            return plaintext_bytes.decode('utf-8', errors='ignore').strip(chr(0))
        except:
            return ""
