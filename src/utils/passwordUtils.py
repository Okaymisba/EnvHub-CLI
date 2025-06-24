import base64
import hashlib
import hmac
import os


class PasswordUtils:
    @staticmethod
    def hash_password(password: str) -> str:

        """
        Hash a password for storing.

        Salts the password with 16 bytes of random data and then applies
        100,000 iterations of HMAC-SHA256 to it. The resulting hash is
        32 bytes long and is base64 encoded for easy storage.

        Args:
            password: The password to hash.

        Returns:
            A base64 encoded string of the hashed password.
        """
        salt = os.urandom(16)
        hash_bytes = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            100_000,
            dklen=32  # 256 bits
        )

        combined = salt + hash_bytes
        return base64.b64encode(combined).decode('utf-8')

    @staticmethod
    def verify_password(password: str, stored_hash: str) -> bool:

        """
        Verify a password against a stored hash.

        Verifies a password against a stored hash produced by
        `hash_password`. The stored hash is expected to be a base64
        encoded string of the form `salt + hash`, where `salt` is 16
        bytes of random data and `hash` is the result of 100,000
        iterations of HMAC-SHA256 using the password and salt.

        Args:
            password: The password to verify.
            stored_hash: The stored hash to verify against.

        Returns:
            True if the password matches the stored hash, False otherwise.
        """
        try:
            combined = base64.b64decode(stored_hash.encode('utf-8'))
            salt = combined[:16]
            stored_hash_bytes = combined[16:]

            derived_hash = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt,
                100_000,
                dklen=32
            )

            return hmac.compare_digest(stored_hash_bytes, derived_hash)
        except Exception as e:
            print("Password verification error:", e)
            return False
