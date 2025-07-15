# Copyright (c) 2025 Misbah Sarfaraz msbahsarfaraz@gmail.com
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
# If a copy of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

import base64
import os

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class PasswordUtils:
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Generates a salted and hashed password using PBKDF2-HMAC-SHA256 for secure password storage.

        This method creates a random cryptographic salt, combines it with the given password,
        and applies the PBKDF2-HMAC-SHA256 algorithm to derive a secure hash. The resulting
        salt and hash are then concatenated and base64-encoded for storage or further processing.

        The salt ensures that even if two users have the same password, their hashes
        will be different. The function uses a fixed set of iterations and hash length
        to provide consistent and strong security.

        :param password: The plaintext password to be securely hashed.
        :type password: str
        :return: A base64-encoded string containing the concatenated salt and password hash.
        :rtype: str
        """
        salt = os.urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        hash_bytes = kdf.derive(password.encode('utf-8'))
        combined = salt + hash_bytes
        return base64.b64encode(combined).decode('utf-8')

    @staticmethod
    def verify_password(password: str, stored_hash: str) -> bool:
        """
        Verify if the provided password matches the stored hash using PBKDF2-HMAC
        and SHA-256 as the hashing algorithm.

        This method decodes the stored hash, extracts the salt and the original hash
        bytes, and derives a new hash from the provided password using the extracted
        salt. It then compares the new hash with the stored one to determine if they
        match.

        :param password: The password input that needs to be verified.
        :type password: str
        :param stored_hash: The base64 encoded string representing the stored
            password hash and salt.
        :type stored_hash: str
        :return: True if the password matches the stored hash, else False.
        :rtype: bool
        """
        try:
            combined = base64.b64decode(stored_hash.encode('utf-8'))
            salt = combined[:16]
            stored_hash_bytes = combined[16:]

            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            derived_hash = kdf.derive(password.encode('utf-8'))

            result = bytes(stored_hash_bytes) == bytes(derived_hash)

            return result
        except Exception as e:
            print("Password verification error:", e)
            return False
