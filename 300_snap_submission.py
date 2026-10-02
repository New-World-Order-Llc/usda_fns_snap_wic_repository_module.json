# Filename: 300_snap_submission.py

from datetime import datetime
from typing import Dict, Any

from 300_network_adapter import NetworkAdapter
from 300_state_manager import StateManager
from 300_audit_logger import AuditLogger
from 300_data_serialization import DataSerializationEngine
from 300_error_recovery import ErrorRecovery


class SNAPSubmissionEngine:
    """
    Deterministic SNAP submission engine for Beast System 3.0 (Module 300).

    Responsibilities:
    - Accept a completed SNAP application payload
    - Serialize it deterministically
    - Submit via NetworkAdapter
    - Store submission result in StateManager
    - Log all events in AuditLogger
    - Provide deterministic fallback on failure
    """

    def __init__(self):
        self.network = NetworkAdapter()
        self.state = StateManager()
        self.audit = AuditLogger()
        self.serializer = DataSerializationEngine()
        self.recovery = ErrorRecovery()

    def submit(self, application: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deterministically submits a SNAP application.
        """

        member_id = application.get("member_id", "UNKNOWN")

        # Serialize application
        serialized_bundle = self.serializer.serialize_pipeline_result(application)

        self.audit.log(
            "snap_application_serialized",
            member_id,
            {
                "timestamp": datetime.utcnow().isoformat(),
                "bundle_keys": list(serialized_bundle.keys())
            }
        )

        # Submit via network adapter (stub endpoint)
        url = "https://state-benefits.example/api/snap/submit"

        self.audit.log(
            "snap_submission_attempt",
            member_id,
            {"url": url}
        )

        try:
            result = self.network._request(url, application)

        except Exception as e:
            result = self.recovery.capture(
                e,
                {
                    "member_id": member_id,
                    "stage": "snap_submission",
                    "application": application
                }
            )

        # Store submission result
        self.state.save_member_state(
            member_id,
            {
                "type": "SNAP_SUBMISSION",
                "application": application,
                "serialized": serialized_bundle,
                "submission_result": result,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

        self.audit.log(
            "snap_submission_completed",
            member_id,
            {
                "timestamp": datetime.utcnow().isoformat(),
                "success": result.get("success", False)
            }
        )

        return {
            "success": result.get("success", False),
            "member_id": member_id,
            "submission_result": result,
            "serialized_bundle": serialized_bundle
        }


# Example deterministic run
if __name__ == "__main__":
    engine = SNAPSubmissionEngine()

    example_application = {
        "member_id": "M-SNAP-001",
        "application_type": "SNAP Benefits Application",
        "version": "1.0",
        "timestamp": datetime.utcnow().isoformat(),
        "applicant": {
            "first_name": "Laura",
            "last_name": "Benson",
            "date_of_birth": "1985-02-14",
            "ssn_last4": "1234"
        },
        "household": {
            "total_household_members": "1",
            "household_member_details": [
                {
                    "name": "Laura Benson",
                    "relationship": "SELF",
                    "date_of_birth": "1985-02-14",
                    "citizenship_status": "US_CITIZEN"
                }
            ]
        },
        "income": {
            "employment_status": "UNEMPLOYED",
            "monthly_gross_income": "0"
        },
        "expenses": {
            "rent_or_mortgage": "750",
            "utilities": "150"
        },
        "signature": {
            "applicant_signature": "Laura Benson",
            "signature_date": datetime.utcnow().isoformat()
        }
    }

    print(engine.submit(example_application))
