from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
import base64
import datetime

class AuthManager:
    def __init__(self, key_id: str, key_file_path: str):
        self.key_id = key_id
        self.private_key = self._load_private_key(key_file_path)

    def _load_private_key(self, file_path: str):
        with open(file_path, "rb") as key_file:
            return serialization.load_pem_private_key(
                key_file.read(),
                password=None
            )

    def generate_headers(self, method: str, path: str) -> dict:
        timestamp = int(datetime.datetime.now().timestamp() * 1000)
        msg_string = str(timestamp) + method + path
        signature = self._sign_message(msg_string)
        
        return {
            'Content-Type': 'application/json',
            'KALSHI-ACCESS-KEY': self.key_id,
            'KALSHI-ACCESS-SIGNATURE': signature,
            'KALSHI-ACCESS-TIMESTAMP': str(timestamp)
        }

    def _sign_message(self, message: str) -> str:
        msg_bytes = message.encode('utf-8')
        signature = self.private_key.sign(
            msg_bytes,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.DIGEST_LENGTH
            ),
            hashes.SHA256()
        )
        return base64.b64encode(signature).decode('utf-8')
