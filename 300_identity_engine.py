# Filename: 300_identity_engine.py

from datetime import datetime
from typing import Dict, Any

from 300_cryptography_layer import BeastCryptographyLayer
from 300_audit_logger import AuditLogger
from 300_error_recovery import ErrorRecovery
from 300_storage_engine import BeastStorageEngine


class BeastIdentityEngine:
    """
    Beast System 3.0 Deterministic Identity Engine (Module 300).

    Responsibilities:
    - Create deterministic member identities
    - Generate cryptographic identity fingerprints
    - Validate identity integrity
    - Manage identity attributes and membership metadata
    - Provide deterministic identity snapshots
    - Guarantee audit logging for all identity operations
    """

    def __init__(self):
        self.crypto = BeastCryptographyLayer()
        self.audit = AuditLogger()
        self.recovery = ErrorRecovery()
        self.storage = BeastStorageEngine(base_path="./beast_identities")

    # ---------------------------------------------------------
    # IDENTITY CREATION
    # ---------------------------------------------------------

    def create_identity(self, member_id: str, attributes: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates a deterministic identity record for a member.
        """

        try:
            fingerprint = self.crypto.hash(member_id + str(attributes))["hash"]

            identity_record = {
                "member_id": member_id,
                "attributes": attributes,
                "fingerprint": fingerprint,
                "created": datetime.utcnow().isoformat()
            }

            self.storage.save_json("identity", member_id, identity_record)

            self.audit.log(
                "identity_created",
                member_id,
                {
                    "timestamp": identity_record["created"],
                    "fingerprint": fingerprint
                }
            )

            return {"success": True, "identity": identity_record}

        except Exception as e:
            return self.recovery.capture(e, {"member_id": member_id, "attributes": attributes})

    # ---------------------------------------------------------
    # IDENTITY VALIDATION
    # ---------------------------------------------------------

    def validate_identity(self, member_id: str) -> Dict[str, Any]:
        """
        Validates the deterministic identity fingerprint.
        """

        try:
            identity = self.storage.load_json("identity", member_id)
            if not identity:
                return {"success": False, "error": "Identity not found"}

            expected = self.crypto.hash(member_id + str(identity["attributes"]))["hash"]
            valid = expected == identity["fingerprint"]

            self.audit.log(
                "identity_validation",
                member_id,
                {
                    "timestamp": datetime.utcnow().isoformat(),
                    "valid": valid
                }
            )

            return {"success": True, "valid": valid, "identity": identity}

        except Exception as e:
            return self.recovery.capture(e, {"member_id": member_id})

    # ---------------------------------------------------------
    # UPDATE IDENTITY ATTRIBUTES
    # ---------------------------------------------------------

    def update_attributes(self, member_id: str, new_attributes: Dict[str, Any]) -> Dict[str, Any]:
        """
        Updates identity attributes deterministically.
        """

        try:
            identity = self.storage.load_json("identity", member_id)
            if not identity:
                return {"success": False, "error": "Identity not found"}

            identity["attributes"].update(new_attributes)
            identity["fingerprint"] = self.crypto.hash(member_id + str(identity["attributes"]))["hash"]
            identity["updated"] = datetime.utcnow().isoformat()

            self.storage.save_json("identity", member_id, identity)

            self.audit.log(
                "identity_updated",
                member_id,
                {
                    "timestamp": identity["updated"],
                    "updated_keys": list(new_attributes.keys())
                }
            )

            return {"success": True, "identity": identity}

        except Exception as e:
            return self.recovery.capture(e, {"member_id": member_id, "new_attributes": new_attributes})

    # ---------------------------------------------------------
    # IDENTITY SNAPSHOT
    # ---------------------------------------------------------

    def snapshot(self, member_id: str) -> Dict[str, Any]:
        """
        Returns deterministic identity snapshot.
        """

        try:
            identity = self.storage.load_json("identity", member_id)
            if not identity:
                return {"success": False, "error": "Identity not found"}

            timestamp = datetime.utcnow().isoformat()

            self.audit.log(
                "identity_snapshot_generated",
                member_id,
                {"timestamp": timestamp}
            )

            return {
                "success": True,
                "timestamp": timestamp,
                "identity": identity
            }

        except Exception as e:
            return self.recovery.capture(e, {"member_id": member_id})


# Example deterministic run
if __name__ == "__main__":
    engine = BeastIdentityEngine()

    print(engine.create_identity("M-TEST-001", {"role": "member", "level": 1}))
    print(engine.validate_identity("M-TEST-001"))
    print(engine.update_attributes("M-TEST-001", {"level": 2}))
    print(engine.snapshot("M-TEST-001"))
