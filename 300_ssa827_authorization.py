# Filename: 300_ssa827_authorization.py

from datetime import datetime
from typing import Dict, Any

from 300_state_manager import StateManager
from 300_audit_logger import AuditLogger
from 300_data_serialization import DataSerializationEngine
from 300_error_recovery import ErrorRecovery
from 300_data_validation import DataValidationEngine
from 300_data_normalization import DataNormalizationEngine


class SSA827AuthorizationEngine:
    """
    Deterministic SSA-827 Authorization Engine for Beast System 3.0 (Module 300).

    SSA-827 = Authorization to Disclose Information to the Social Security Administration.

    Responsibilities:
    - Accept member profile + provider list
    - Normalize and validate data
    - Build deterministic SSA-827 authorization payload (NOT copyrighted form)
    - Serialize and store in StateManager
    - Log all events in AuditLogger
    - Provide deterministic fallback on failure
    """

    def __init__(self):
        self.state = StateManager()
        self.audit = AuditLogger()
        self.serializer = DataSerializationEngine()
        self.recovery = ErrorRecovery()
        self.validator = DataValidationEngine()
        self.normalizer = DataNormalizationEngine()

    def build_authorization(self, member_profile: Dict[str, Any], providers: Dict[str, Any]) -> Dict[str, Any]:
        """
        Builds a deterministic SSA-827 authorization payload.
        """

        member_id = member_profile.get("member_id", "UNKNOWN")

        # Normalize profile
        normalized = self.normalizer.normalize_profile(member_profile)

        # Validate profile
        validation = self.validator.validate_profile(normalized)
        if not validation["valid"]:
            self.audit.log(
                "ssa827_validation_failed",
                member_id,
                validation
            )
            return {
                "success": False,
                "member_id": member_id,
                "errors": validation["errors"]
            }

        # Build SSA-827 payload (original structure, not copyrighted)
        payload = {
            "member_id": member_id,
            "application_type": "SSA-827 Authorization",
            "version": "1.0",
            "timestamp": datetime.utcnow().isoformat(),
            "applicant": {
                "first_name": normalized.get("first_name", ""),
                "last_name": normalized.get("last_name", ""),
                "date_of_birth": normalized.get("date_of_birth", ""),
                "ssn_last4": normalized.get("ssn_last4", "")
            },
            "authorized_providers": providers.get("providers", []),
            "authorization_scope": {
                "release_medical_records": True,
                "release_mental_health_records": True,
                "release_hospital_records": True,
                "release_diagnostic_tests": True,
                "release_treatment_plans": True
            },
            "signature": {
                "applicant_signature": "",
                "signature_date": ""
            }
        }

        # Serialize
        serialized = self.serializer.serialize_pipeline_result(payload)

        # Store state
        self.state.save_member_state(
            member_id,
            {
                "type": "SSA827_AUTHORIZATION",
                "data": payload,
                "serialized": serialized,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

        self.audit.log(
            "ssa827_authorization_built",
            member_id,
            {
                "timestamp": datetime.utcnow().isoformat(),
                "application_type": payload["application_type"]
            }
        )

        return {
            "success": True,
            "member_id": member_id,
            "payload": payload,
            "serialized_bundle": serialized
        }


# Example deterministic run
if __name__ == "__main__":
    engine = SSA827AuthorizationEngine()

    profile = {
        "member_id": "M-SSA-001",
        "first_name": "Laura",
        "last_name": "Benson",
        "date_of_birth": "1985-02-14",
        "ssn_last4": "1234"
    }

    providers = {
        "providers": [
            {"name": "Dr. Smith", "facility": "Terre Haute Regional"},
            {"name": "Dr. Lee", "facility": "Pain Management Clinic"},
            {"name": "Dr. Patel", "facility": "Orthopedic Center"}
        ]
    }

    print(engine.build_authorization(profile, providers))
