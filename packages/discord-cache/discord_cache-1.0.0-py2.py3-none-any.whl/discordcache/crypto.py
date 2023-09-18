import hashlib
import os

from typing import Any

from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2


class Crypto:
    """
    # Crypto

    ---
    Parameters:
        - path: str
            Path to encrypted file

    Methods:
        - salt(data: Any) -> None
            Salting data
        - encrypt(data: Any, password: str) -> None
            Encrypting data
        - decrypt(password: str) -> None
            Decrypting data

    """

    def __init__(self, path: str) -> None:
        self.path = path

    def salt(self, data: Any) -> None:
        """
        # Salting

        ---
        Parameters:
            - data: Any
                Data to salt

        Returns:
            - salted_message: bytes
                Salted data
        """
        salt = os.urandom(16)
        salted_message = salt + data.encode("utf-8")

        hashed_message = hashlib.sha256(salted_message).hexdigest()

        return hashed_message

    def encrypt(self, data: Any, password: str) -> None:
        """
        # Encrypting

        ---
        Parameters:
            - data: Any
                Data to encrypt
            - password: str
                Password to encrypt data
            - file: str
                File to write encrypted data

        Returns:
            - encrypted_data: bytes
                Encrypted data
            - tag: bytes
                Tag to verify data
        """
        salt_password = PBKDF2(password, self.salt(password), dkLen=32)
        salt_data = self.salt(data).encode("utf-8")

        cipher = AES.new(salt_password, AES.MODE_EAX)

        encrypted_data, tag = cipher.encrypt_and_digest(salt_data)

        with open(self.path, "wb") as f:
            f.write(encrypted_data)

        return encrypted_data

    def decrypt(self, password: str) -> None:
        """
        # Decrypting

        ---
        Parameters:
            - file: str
                File to decrypt
            - password: str
                Password to decrypt data

        Returns:
            - decrypted_data: bytes
                Decrypted data
        """
        salt_password = PBKDF2(password, self.salt(password), dkLen=32)

        with open(self.path, "rb") as f:
            encrypted_data = f.read()

        cipher = AES.new(salt_password, AES.MODE_EAX)

        decrypted_data = cipher.decrypt(encrypted_data)

        return decrypted_data