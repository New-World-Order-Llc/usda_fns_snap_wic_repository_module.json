# Filename: 300_unemployment_intake.py

from datetime import datetime
from typing import Dict, Any

from 300_state_manager import StateManager
from 300_audit_logger import AuditLogger
from 300_data_normalization import DataNormalizationEngine
from 300_data_validation import DataValidationEngine
from 300_data_serialization import DataSerializationEngine
from 300_error_recovery import ErrorRecovery


class UnemploymentIntakeEngine:
    """
    Deterministic Unemployment Insurance Intake Engine for Beast System 3.0 (Module 300).

    Supports:
    - Initial unemployment claim intake
    - Loss-of-work verification
    - Employer separation details
    - Weekly benefit eligibility baseline

    Responsibilities:
    - Accept claimant profile + separation details + work history
    - Normalize and validate data
    - Build deterministic unemployment intake payload (NOT copyrighted form)
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

    def build_intake(self, claimant_profile: Dict[str, Any], separation_data: Dict[str, Any], work_history: Dict[str, Any]) -> Dict[str, Any]:
        """
        Builds a deterministic unemployment insurance intake payload.
        """

        member_id = claimant_profile.get("member_id", "UNKNOWN")

        # Normalize profile
        normalized = self.normalizer.normalize_profile(claimant_profile)

        # Validate profile
        validation = self.validator.validate_profile(normalized)
        if not validation["valid"]:
            self.audit.log(
                "unemployment_validation_failed",
                member_id,
                validation
            )
            return {
                "success": False,
                "member_id": member_id,
                "errors": validation["errors"]
            }

        # Build deterministic unemployment intake payload
        payload = {
            "member_id": member_id,
            "application_type": "Unemployment Insurance Intake",
            "version": "1.0",
            "timestamp": datetime.utcnow().isoformat(),
            "claimant": {
                "first_name": normalized.get("first_name", ""),
                "last_name": normalized.get("last_name", ""),
                "date_of_birth": normalized.get("date_of_birth", ""),
                "ssn_last4": normalized.get("ssn_last4", "")
            },
            "separation": {
                "last_employer": separation_data.get("last_employer", ""),
                "last_day_worked": separation_data.get("last_day_worked", ""),
                "reason_for_separation": separation_data.get("reason_for_separation", ""),
                "eligible_for_rehire": separation_data.get("eligible_for_rehire", False)
            },
            "work_history": work_history.get("jobs", []),
            "income": {
                "weekly_wages": work_history.get("weekly_wages", ""),
                "employment_status": "UNEMPLOYED"
            },
            "signature": {
                "claimant_signature": "",
                "signature_date": ""
            }
        }

        # Serialize
        serialized = self.serializer.serialize_pipeline_result(payload)

        # Store state
        self.state.save_member_state(
            member_id,
            {
                "type": "UNEMPLOYMENT_INTAKE",
                "data": payload,
                "serialized": serialized,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

        self.audit.log(
            "unemployment_intake_built",
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
    engine = UnemploymentIntakeEngine()

    claimant_profile = {
        "member_id": "M-UI-001",
        "first_name": "Laura",
        "last_name": "Benson",
        "date_of_birth": "1985-02-14",
        "ssn_last4": "1234"
    }

    separation_data = {
        "last_employer": "Warehouse Co",
        "last_day_worked": "2024-06-30",
        "reason_for_separation": "Medical inability to continue duties",
        "eligible_for_rehire": False
    }

    work_history = {
        "jobs": [
            {"employer": "Warehouse Co", "position": "Loader", "years": 5}
        ],
        "weekly_wages": "0"
    }

    print(engine.build_intake(claimant_profile, separation_data, work_history))
