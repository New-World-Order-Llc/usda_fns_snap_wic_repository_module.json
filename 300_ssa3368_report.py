# Filename: 300_ssa3368_report.py

from datetime import datetime
from typing import Dict, Any

from 300_state_manager import StateManager
from 300_audit_logger import AuditLogger
from 300_data_normalization import DataNormalizationEngine
from 300_data_validation import DataValidationEngine
from 300_data_serialization import DataSerializationEngine
from 300_error_recovery import ErrorRecovery


class SSA3368ReportEngine:
    """
    Deterministic SSA-3368 Disability Report Engine for Beast System 3.0 (Module 300).

    SSA-3368 = Disability Report (Adult)
    Contains:
    - Medical treatment history
    - Functional limitations
    - Work activity
    - Daily living impacts
    - Assistive devices
    - Hospitalizations
    - Medications
    - Diagnostic tests

    Responsibilities:
    - Accept raw medical + functional data
    - Normalize and validate
    - Build deterministic SSA-3368 payload (NOT copyrighted form)
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

    def build_report(self, member_profile: Dict[str, Any], medical_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Builds a deterministic SSA-3368 disability report payload.
        """

        member_id = member_profile.get("member_id", "UNKNOWN")

        # Normalize profile
        normalized = self.normalizer.normalize_profile(member_profile)

        # Validate profile
        validation = self.validator.validate_profile(normalized)
        if not validation["valid"]:
            self.audit.log(
                "ssa3368_validation_failed",
                member_id,
                validation
            )
            return {
                "success": False,
                "member_id": member_id,
                "errors": validation["errors"]
            }

        # Build SSA-3368 payload (original structure, not copyrighted)
        payload = {
            "member_id": member_id,
            "application_type": "SSA-3368 Disability Report",
            "version": "1.0",
            "timestamp": datetime.utcnow().isoformat(),
            "applicant": {
                "first_name": normalized.get("first_name", ""),
                "last_name": normalized.get("last_name", ""),
                "date_of_birth": normalized.get("date_of_birth", ""),
                "ssn_last4": normalized.get("ssn_last4", "")
            },
            "medical_conditions": medical_data.get("conditions", []),
            "treatment_providers": medical_data.get("providers", []),
            "hospitalizations": medical_data.get("hospitalizations", []),
            "medications": medical_data.get("medications", []),
            "diagnostic_tests": medical_data.get("diagnostic_tests", []),
            "functional_limitations": medical_data.get("functional_limitations", ""),
            "daily_activities": medical_data.get("daily_activities", ""),
            "assistive_devices": medical_data.get("assistive_devices", []),
            "work_activity": medical_data.get("work_activity", []),
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
                "type": "SSA3368_REPORT",
                "data": payload,
                "serialized": serialized,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

        self.audit.log(
            "ssa3368_report_built",
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
    engine = SSA3368ReportEngine()

    profile = {
        "member_id": "M-SSA-001",
        "first_name": "Laura",
        "last_name": "Benson",
        "date_of_birth": "1985-02-14",
        "ssn_last4": "1234"
    }

    medical = {
        "conditions": [
            "Severe spinal injury",
            "Chronic pain",
            "Limited mobility"
        ],
        "providers": [
            {"name": "Dr. Smith", "specialty": "Orthopedics"},
            {"name": "Dr. Lee", "specialty": "Pain Management"}
        ],
        "hospitalizations": [
            {"facility": "Terre Haute Regional", "date": "2024-07-02"}
        ],
        "medications": [
            {"name": "Gabapentin", "dose": "300mg", "frequency": "3x/day"}
        ],
        "diagnostic_tests": [
            {"type": "MRI", "date": "2024-07-10", "finding": "Lumbar disc damage"}
        ],
        "functional_limitations": "Cannot lift more than 5 lbs; cannot stand longer than 10 minutes.",
        "daily_activities": "Requires assistance with bathing, cooking, and cleaning.",
        "assistive_devices": ["Back brace", "Cane"],
        "work_activity": [
            {"employer": "Warehouse Co", "position": "Loader", "last_day": "2024-06-30"}
        ]
    }

    print(engine.build_report(profile, medical))
