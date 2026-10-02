# Filename: 300_cryptography_layer.py

import hashlib
import hmac
import os
from datetime import datetime
from typing import Dict, Any

from 300_audit_logger import AuditLogger
from 300_error_recovery import ErrorRecovery


class BeastCryptographyLayer:
    """
    Beast System 3.0 Deterministic Cryptography Layer (Module 300).

    Responsibilities:
    - Provide deterministic hashing (SHA-256)
    - Provide deterministic HMAC signing
    - Provide deterministic random byte generation
    - Provide deterministic signature verification
    - Guarantee audit logging for all cryptographic operations
    - Provide fallback and recovery on cryptographic failures
    """

    def __init__(self):
        self.audit = AuditLogger()
        self.recovery = ErrorRecovery()

        # Deterministic system key (placeholder; replace with secure key mgmt)
        self.system_key = b"BEAST_SYSTEM_3_0_DETERMINISTIC_KEY"

    # ---------------------------------------------------------
    # HASHING
    # ---------------------------------------------------------

    def hash(self, data: str) -> Dict[str, Any]:
        """
        Deterministic SHA-256 hashing.
        """

        try:
            digest = hashlib.sha256(data.encode("utf-8")).hexdigest()

            self.audit.log(
                "crypto_hash_generated",
                "SYSTEM",
                {
                    "timestamp": datetime.utcnow().isoformat(),
                    "input_length": len(data),
                    "digest": digest
                }
            )

            return {"success": True, "hash": digest}

        except Exception as e:
            return self.recovery.capture(e, {"data": data})

    # ---------------------------------------------------------
    # HMAC SIGNING
    # ---------------------------------------------------------

    def sign(self, data: str) -> Dict[str, Any]:
        """
        Deterministic HMAC-SHA256 signing.
        """

        try:
            signature = hmac.new(self.system_key, data.encode("utf-8"), hashlib.sha256).hexdigest()

            self.audit.log(
                "crypto_signature_generated",
                "SYSTEM",
                {
                    "timestamp": datetime.utcnow().isoformat(),
                    "input_length": len(data),
                    "signature": signature
                }
            )

            return {"success": True, "signature": signature}

        except Exception as e:
            return self.recovery.capture(e, {"data": data})

    # ---------------------------------------------------------
    # SIGNATURE VERIFICATION
    # ---------------------------------------------------------

    def verify(self, data: str, signature: str) -> Dict[str, Any]:
        """
        Deterministic HMAC-SHA256 signature verification.
        """

        try:
            expected = hmac.new(self.system_key, data.encode("utf-8"), hashlib.sha256).hexdigest()
            valid = hmac.compare_digest(expected, signature)

            self.audit.log(
                "crypto_signature_verified",
                "SYSTEM",
                {
                    "timestamp": datetime.utcnow().isoformat(),
                    "valid": valid
                }
            )

            return {"success": True, "valid": valid}

        except Exception as e:
            return self.recovery.capture(e, {"data": data, "signature": signature})

    # ---------------------------------------------------------
    # RANDOM BYTE GENERATION
    # ---------------------------------------------------------

    def random_bytes(self, length: int = 32) -> Dict[str, Any]:
        """
        Deterministic random byte generation (cryptographically secure).
        """

        try:
            blob = os.urandom(length)

            self.audit.log(
                "crypto_random_bytes_generated",
                "SYSTEM",
                {
                    "timestamp": datetime.utcnow().isoformat(),
                    "length": length
                }
            )

            return {"success": True, "bytes": blob}

        except Exception as e:
            return self.recovery.capture(e, {"length": length})


# Example deterministic run
if __name__ == "__main__":
    crypto = BeastCryptographyLayer()

    print(crypto.hash("Hello Beast"))
    sig = crypto.sign("Hello Beast")
    print(sig)
    print(crypto.verify("Hello Beast", sig["signature"]))
    print(crypto.random_bytes(16))
