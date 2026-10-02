# Filename: 300_security_layer.py

from datetime import datetime
from typing import Dict, Any

from 300_audit_logger import AuditLogger
from 300_error_recovery import ErrorRecovery


class BeastSecurityLayer:
    """
    Beast System 3.0 Deterministic Security Layer (Module 300).

    Responsibilities:
    - Enforce deterministic access control
    - Validate operator actions
    - Protect sensitive benefit data
    - Provide deterministic authorization decisions
    - Log all security events
    - Provide fallback and recovery on security failures
    """

    def __init__(self):
        self.audit = AuditLogger()
        self.recovery = ErrorRecovery()

        # Deterministic role registry
        self.roles = {
            "operator": {
                "permissions": [
                    "run_pipeline",
                    "run_sync",
                    "publish_event",
                    "inspect_state",
                    "inspect_audit",
                    "run_scheduler"
                ]
            },
            "system": {
                "permissions": [
                    "internal_execution",
                    "scheduler_execution",
                    "event_bus_execution"
                ]
            },
            "restricted": {
                "permissions": []
            }
        }

    # ---------------------------------------------------------
    # ROLE CHECK
    # ---------------------------------------------------------

    def has_permission(self, role: str, permission: str) -> bool:
        """
        Deterministic permission check.
        """

        allowed = permission in self.roles.get(role, {}).get("permissions", [])

        self.audit.log(
            "security_permission_check",
            role,
            {
                "timestamp": datetime.utcnow().isoformat(),
                "role": role,
                "permission": permission,
                "allowed": allowed
            }
        )

        return allowed

    # ---------------------------------------------------------
    # AUTHORIZATION GATE
    # ---------------------------------------------------------

    def authorize(self, role: str, permission: str) -> Dict[str, Any]:
        """
        Deterministic authorization gate.
        """

        if self.has_permission(role, permission):
            return {"success": True, "role": role, "permission": permission}

        self.audit.log(
            "security_authorization_denied",
            role,
            {
                "timestamp": datetime.utcnow().isoformat(),
                "role": role,
                "permission": permission
            }
        )

        return {
            "success": False,
            "error": "Permission denied",
            "role": role,
            "permission": permission
        }

    # ---------------------------------------------------------
    # INPUT VALIDATION
    # ---------------------------------------------------------

    def validate_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deterministic payload validation.
        Ensures no forbidden keys, no nulls, no unsafe structures.
        """

        forbidden_keys = ["password", "token", "secret"]
        errors = []

        for key, value in payload.items():
            if key in forbidden_keys:
                errors.append(f"Forbidden key: {key}")
            if value is None:
                errors.append(f"Null value not allowed: {key}")

        if errors:
            self.audit.log(
                "security_payload_validation_failed",
                payload.get("member_id", "SYSTEM"),
                {
                    "timestamp": datetime.utcnow().isoformat(),
                    "errors": errors
                }
            )

            return {
                "success": False,
                "errors": errors
            }

        self.audit.log(
            "security_payload_validation_passed",
            payload.get("member_id", "SYSTEM"),
            {"timestamp": datetime.utcnow().isoformat()}
        )

        return {"success": True}

    # ---------------------------------------------------------
    # SECURITY SNAPSHOT
    # ---------------------------------------------------------

    def snapshot(self) -> Dict[str, Any]:
        """
        Returns deterministic security configuration snapshot.
        """

        timestamp = datetime.utcnow().isoformat()

        snapshot = {
            "timestamp": timestamp,
            "roles": self.roles
        }

        self.audit.log(
            "security_snapshot_generated",
            "SYSTEM",
            {"timestamp": timestamp}
        )

        return snapshot


# Example deterministic run
if __name__ == "__main__":
    sec = BeastSecurityLayer()

    print(sec.authorize("operator", "run_pipeline"))
    print(sec.authorize("restricted", "run_pipeline"))

    print(sec.validate_payload({"member_id": "M-TEST-001", "data": "ok"}))
    print(sec.validate_payload({"member_id": "M-TEST-001", "password": "123"}))

    print(sec.snapshot())
