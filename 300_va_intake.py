# Filename: 300_va_intake.py

from datetime import datetime
from typing import Dict, Any

from 300_state_manager import StateManager
from 300_audit_logger import AuditLogger
from 300_data_normalization import DataNormalizationEngine
from 300_data_validation import DataValidationEngine
from 300_data_serialization import DataSerializationEngine
from 300_error_recovery import ErrorRecovery


class VAIntakeEngine:
    """
    Deterministic Veterans Benefits Intake Engine for Beast System 3.0 (Module 300).

    Supports:
    - VA Disability Intake (non‑copyrighted structure)
    - VA Healthcare Enrollment Intake
    - Service‑Connected Injury Intake

    Responsibilities:
    - Accept veteran profile + service history + medical issues
    - Normalize and validate data
    - Build deterministic VA intake payload
    - Serialize and store in StateManager
    - Log all events in AuditLogger
    - Provide deterministic fallback on failure
    """

    def __init__(self):
        self.state = StateManager()
        self.audit = AuditLogger()
        self.normalizer = DataNormalizationEngine()
        self.validator = DataValidationEngine()
        self.serializer = DataSerializationEngine()
        self.recovery = ErrorRecovery()

    def build_intake(self, veteran_profile: Dict[str, Any], service_data: Dict[str, Any], medical_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Builds a deterministic VA intake payload.
        """

        member_id = veteran_profile.get("member_id", "UNKNOWN")

        # Normalize profile
        normalized = self.normalizer.normalize_profile(veteran_profile)

        # Validate profile
        validation = self.validator.validate_profile(normalized)
        if not validation["valid"]:
            self.audit.log(
                "va_intake_validation_failed",
                member_id,
                validation
            )
            return {
                "success": False,
                "member_id": member_id,
                "errors": validation["errors"]
            }

        # Build deterministic VA intake payload (NOT copyrighted)
        payload = {
            "member_id": member_id,
            "application_type": "VA Benefits Intake",
            "version": "1.0",
            "timestamp": datetime.utcnow().isoformat(),
            "veteran": {
                "first_name": normalized.get("first_name", ""),
                "last_name": normalized.get("last_name", ""),
                "date_of_birth": normalized.get("date_of_birth", ""),
                "ssn_last4": normalized.get("ssn_last4", ""),
                "branch": service_data.get("branch", ""),
                "service_start": service_data.get("service_start", ""),
                "service_end": service_data.get("service_end", ""),
                "discharge_status": service_data.get("discharge_status", "")
            },
            "service_connected_conditions": medical_data.get("conditions", []),
            "hospitalizations": medical_data.get("hospitalizations", []),
            "medications": medical_data.get("medications", []),
            "functional_limitations": medical_data.get("functional_limitations", ""),
            "daily_impacts": medical_data.get("daily_impacts", ""),
            "signature": {
                "veteran_signature": "",
                "signature_date": ""
            }
        }

        # Serialize
        serialized = self.serializer.serialize_pipeline_result(payload)

        # Store state
        self.state.save_member_state(
            member_id,
            {
                "type": "VA_INTAKE",
                "data": payload,
                "serialized": serialized,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

        self.audit.log(
            "va_intake_built",
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
    engine = VAIntakeEngine()

    veteran_profile = {
        "member_id": "M-VA-001",
        "first_name": "James",
        "last_name": "Carter",
        "date_of_birth": "1978-03-22",
        "ssn_last4": "9876"
    }

    service_data = {
        "branch": "Army",
        "service_start": "1998-06-01",
        "service_end": "2006-06-01",
        "discharge_status": "Honorable"
    }

    medical_data = {
        "conditions": [
            "Service-connected knee injury",
            "PTSD"
        ],
        "hospitalizations": [
            {"facility": "VA Medical Center", "date": "2024-05-10"}
        ],
        "medications": [
