# Filename: 300_network_gateway.py

import json
import ssl
import urllib.request
from datetime import datetime
from typing import Dict, Any

from 300_security_layer import BeastSecurityLayer
from 300_audit_logger import AuditLogger
from 300_error_recovery import ErrorRecovery


class BeastNetworkGateway:
    """
    Beast System 3.0 Deterministic Network Gateway (Module 300).

    Responsibilities:
    - Provide deterministic outbound network requests
    - Enforce security-layer authorization
    - Validate payloads before transmission
    - Guarantee audit logging for all network operations
    - Provide deterministic fallback and recovery on network failure
    - Replace NetworkAdapter with a hardened, deterministic gateway
    """

    def __init__(self):
        self.security = BeastSecurityLayer()
        self.audit = AuditLogger()
        self.recovery = ErrorRecovery()

        # Deterministic SSL context
        self.ssl_context = ssl.create_default_context()

    # ---------------------------------------------------------
    # OUTBOUND REQUEST
    # ---------------------------------------------------------

    def request(self, role: str, url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deterministic outbound request with full security validation.
        """

        # Authorization gate
        auth = self.security.authorize(role, "internal_execution")
        if not auth["success"]:
            return auth

        # Payload validation
        validation = self.security.validate_payload(payload)
        if not validation["success"]:
            return validation

        timestamp = datetime.utcnow().isoformat()

        self.audit.log(
            "network_gateway_request_start",
            payload.get("member_id", "SYSTEM"),
            {
                "timestamp": timestamp,
                "url": url,
                "payload_keys": list(payload.keys())
            }
        )

        try:
            data = json.dumps(payload).encode("utf-8")

            req = urllib.request.Request(
                url,
                data=data,
                headers={"Content-Type": "application/json"},
                method="POST"
            )

            with urllib.request.urlopen(req, context=self.ssl_context) as response:
                raw = response.read().decode("utf-8")
                parsed = json.loads(raw)

            self.audit.log(
                "network_gateway_request_success",
                payload.get("member_id", "SYSTEM"),
                {
                    "timestamp": datetime.utcnow().isoformat(),
                    "url": url
                }
            )

            return {
                "success": True,
                "url": url,
                "response": parsed
            }

        except Exception as e:
            recovery = self.recovery.capture(
                e,
                {
                    "url": url,
                    "payload": payload,
                    "role": role
                }
            )

            self.audit.log(
                "network_gateway_request_failure",
                payload.get("member_id", "SYSTEM"),
                {
                    "timestamp": datetime.utcnow().isoformat(),
                    "url": url,
                    "error": str(e)
                }
            )

            return {
                "success": False,
                "error": str(e),
                "recovery": recovery
            }

    # ---------------------------------------------------------
    # INBOUND VALIDATION (stub)
    # ---------------------------------------------------------

    def validate_inbound(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deterministic inbound payload validation.
        """

        validation = self.security.validate_payload(payload)

        self.audit.log(
            "network_gateway_inbound_validation",
            payload.get("member_id", "SYSTEM"),
            {
                "timestamp": datetime.utcnow().isoformat(),
                "valid": validation["success"]
            }
        )

        return validation


# Example deterministic run
if __name__ == "__main__":
    gateway = BeastNetworkGateway()

    payload = {
        "member_id": "M-TEST-001",
        "message": "Hello world"
    }

    print(gateway.request("system", "https://example.com/api/test", payload))
