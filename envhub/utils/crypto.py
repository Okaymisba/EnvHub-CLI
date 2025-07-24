# Copyright (c) 2025 Misbah Sarfaraz msbahsarfaraz@gmail.com
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
# If a copy of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

import base64
import os

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class CryptoUtils:
    @staticmethod
    def _to_bytes(data: str) -> bytes:
        return data.encode('utf-8')

    @staticmethod
    def _to_str(data: bytes) -> str:
        return data.decode('utf-8')

    @staticmethod
    def _b64encode(data: bytes) -> str:
        return base64.b64encode(data).decode('utf-8')

    @staticmethod
    def _b64decode(data: str) -> bytes:
        return base64.b64decode(data.encode('utf-8'))

    @staticmethod
    def derive_key(password: str, salt: bytes) -> bytes:
        """
        Derive a key from the given password and salt using PBKDF2 with HMAC-SHA256.

        Args:
            password: The password to use for key derivation.
            salt: The salt to use for key derivation.

        Returns:
            A 32 byte key derived from the given password and salt.
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,  # AES-256
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        return kdf.derive(CryptoUtils._to_bytes(password))

    @staticmethod
    def encrypt(content: str, password: str) -> dict:
        """
        Encrypt the given content using the given password.

        The password is used to derive a key using PBKDF2 with HMAC-SHA256.
        The derived key is then used to encrypt the content using AES-GCM with a random nonce.

        The following information is returned in a dictionary:
            - `ciphertext`: The encrypted content (base64 encoded).
            - `tag`: The authentication tag (base64 encoded).
            - `salt`: The salt used for key derivation (base64 encoded).
            - `nonce`: The nonce used for encryption (base64 encoded).

        Args:
            content: The content to encrypt.
            password: The password to use for key derivation.

        Returns:
            A dictionary containing the encrypted content, authentication tag, salt, and nonce.
        """
        salt = os.urandom(16)
        nonce = os.urandom(12)  # GCM nonce size
        key = CryptoUtils.derive_key(password, salt)
        aesgcm = AESGCM(key)

        content_bytes = CryptoUtils._to_bytes(content)
        encrypted = aesgcm.encrypt(nonce, content_bytes, None)

        return {
            "ciphertext": CryptoUtils._b64encode(encrypted[:-16]),
            "tag": CryptoUtils._b64encode(encrypted[-16:]),
            "salt": CryptoUtils._b64encode(salt),
            "nonce": CryptoUtils._b64encode(nonce)
        }

    @staticmethod
    def decrypt(encrypted_data: dict, password: str) -> str:
        """
        Decrypt the given encrypted data using the given password.

        The password is used to derive a key using PBKDF2 with HMAC-SHA256.
        The derived key is then used to decrypt the content using AES-GCM with the given nonce.

        Args:
            encrypted_data: The encrypted data to decrypt, containing the following keys:
                - `ciphertext`: The encrypted content (base64 encoded).
                - `tag`: The authentication tag (base64 encoded).
                - `salt`: The salt used for key derivation (base64 encoded).
                - `nonce`: The nonce used for encryption (base64 encoded).
            password: The password to use for key derivation.

        Returns:
            The decrypted content as a string.
        """
        salt = CryptoUtils._b64decode(encrypted_data["salt"])
        nonce = CryptoUtils._b64decode(encrypted_data["nonce"])
        ciphertext = CryptoUtils._b64decode(encrypted_data["ciphertext"])
        tag = CryptoUtils._b64decode(encrypted_data["tag"])

        encrypted = ciphertext + tag
        key = CryptoUtils.derive_key(password, salt)
        aesgcm = AESGCM(key)
        decrypted = aesgcm.decrypt(nonce, encrypted, None)

        return CryptoUtils._to_str(decrypted)

    @staticmethod
    def decrypt_env_file(env_file_path: str, password: str) -> dict:
        """
        Decrypts a given .env file and returns decrypted environment variables.
        Fails immediately if any decryption fails.

        :param env_file_path: Path to the .env file to be processed
        :param password: Password used for decryption
        :return: Dictionary of decrypted environment variables
        :raises: ValueError if decryption fails for any variable
        :raises: IOError if file cannot be read
        """
        if not os.path.exists(env_file_path):
            raise FileNotFoundError(f"Environment file not found: {env_file_path}")

        if not password:
            raise ValueError("No password provided for decryption")

        decrypted_envs = {}

        try:
            with open(env_file_path, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue

                    if '=' not in line:
                        raise ValueError(f"Invalid format in line {line_num}: Missing '=' in line")

                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()

                    if not key:
                        raise ValueError(f"Empty key in line {line_num}")

                    if ':' in value:
                        parts = value.split(':')
                        if len(parts) != 4:
                            raise ValueError(
                                f"Invalid encrypted value format for {key}. "
                            )

                        try:
                            encrypted_data = {
                                "ciphertext": parts[0],
                                "salt": parts[1],
                                "nonce": parts[2],
                                "tag": parts[3]
                            }
                            decrypted_envs[key] = CryptoUtils.decrypt(encrypted_data, password)
                        except Exception as e:
                            raise ValueError(
                                f"Failed to decrypt environment variable '{key}': {str(e)}"
                            ) from e
                    else:
                        raise ValueError(
                            f"Invalid encrypted value format for {key}. "
                        )

        except IOError as e:
            raise IOError(f"Failed to read environment file '{env_file_path}': {str(e)}") from e

        return decrypted_envs
