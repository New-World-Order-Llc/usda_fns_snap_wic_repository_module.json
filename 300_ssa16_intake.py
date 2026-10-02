# Filename: 300_ssa16_intake.py

from datetime import datetime
from typing import Dict, Any

from 300_state_manager import StateManager
from 300_audit_logger import AuditLogger
from 300_data_normalization import DataNormalizationEngine
from 300_data_validation import DataValidationEngine
from 300_data_serialization import DataSerializationEngine
from 300_error_recovery import ErrorRecovery


class SSA16IntakeEngine:
    """
    Deterministic SSA-16 Intake Engine for Beast System 3.0 (Module 300).

    SSA-16 = Application for Disability Insurance Benefits.

    Responsibilities:
    - Accept raw member profile + disability details
    - Normalize and validate data
    - Build deterministic SSA-16 intake payload (NOT copyrighted form)
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

    def build_intake(self, member_profile: Dict[str, Any], disability_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Builds a deterministic SSA-16 intake payload.
        """

        member_id = member_profile.get("member_id", "UNKNOWN")

        # Normalize profile
        normalized = self.normalizer.normalize_profile(member_profile)

        # Validate profile
        validation = self.validator.validate_profile(normalized)
        if not validation["valid"]:
            self.audit.log(
                "ssa16_validation_failed",
                member_id,
                validation
            )
            return {
                "success": False,
                "member_id": member_id,
                "errors": validation["errors"]
            }

        # Build SSA-16 intake payload (original structure, not copyrighted)
        payload = {
            "member_id": member_id,
            "application_type": "SSA-16 Disability Intake",
            "version": "1.0",
            "timestamp": datetime.utcnow().isoformat(),
            "applicant": {
                "first_name": normalized.get("first_name", ""),
                "last_name": normalized.get("last_name", ""),
                "date_of_birth": normalized.get("date_of_birth", ""),
                "ssn_last4": normalized.get("ssn_last4", ""),
                "citizenship_status": normalized.get("citizenship_status", "")
            },
            "disability": {
                "onset_date": disability_data.get("onset_date", ""),
                "primary_condition": disability_data.get("primary_condition", ""),
                "secondary_conditions": disability_data.get("secondary_conditions", []),
                "treatment_providers": disability_data.get("treatment_providers", []),
                "work_limitations": disability_data.get("work_limitations", "")
            },
            "work_history": disability_data.get("work_history", []),
            "income": {
                "monthly_gross_income": disability_data.get("monthly_gross_income", ""),
                "employment_status": disability_data.get("employment_status", "")
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
                "type": "SSA16_INTAKE",
                "data": payload,
                "serialized": serialized,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

        self.audit.log(
            "ssa16_intake_built",
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
    engine = SSA16IntakeEngine()

    profile = {
        "member_id": "M-SSA-001",
        "first_name": "Laura",
        "last_name": "Benson",
        "date_of_birth": "1985-02-14",
        "ssn_last4": "1234",
        "citizenship_status": "US_CITIZEN"
    }

    disability = {
        "onset_date": "2024-07-01",
        "primary_condition": "Severe spinal injury",
        "secondary_conditions": ["Chronic pain", "Limited mobility"],
        "treatment_providers": [
            {"name": "Dr. Smith", "specialty": "Orthopedics"},
            {"name": "Dr. Lee", "specialty": "Pain Management"}
        ],
        "work_limitations": "Unable to stand or lift for extended periods",
        "work_history": [
            {"employer": "Warehouse Co", "position": "Loader", "years": 5}
        ],
        "monthly_gross_income": "0",
        "employment_status": "UNEMPLOYED"
    }

    print(engine.build_intake(profile, disability))
