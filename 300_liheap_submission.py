# Filename: 300_liheap_submission.py

from datetime import datetime
from typing import Dict, Any

from 300_network_adapter import NetworkAdapter
from 300_state_manager import StateManager
from 300_audit_logger import AuditLogger
from 300_error_recovery import ErrorRecovery
from 300_data_serialization import DataSerializationEngine


class LIHEAPSubmissionEngine:
    """
    Deterministic LIHEAP (Energy Assistance) submission engine for Beast System 3.0 (Module 300).

    Supports:
    - Heating assistance
    - Cooling assistance
    - Crisis energy assistance

    Responsibilities:
    - Accept a completed LIHEAP application payload
    - Serialize it deterministically
    - Submit via NetworkAdapter (stub endpoint)
    - Store submission result in StateManager
    - Log all events in AuditLogger
    - Provide deterministic fallback on failure
    """

    def __init__(self):
        self.network = NetworkAdapter()
        self.state = StateManager()
        self.audit = AuditLogger()
        self.recovery = ErrorRecovery()
        self.serializer = DataSerializationEngine()

    def submit(self, application: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deterministically submits a LIHEAP application.
        """

        member_id = application.get("member_id", "UNKNOWN")

        # Serialize application
        serialized_bundle = self.serializer.serialize_pipeline_result(application)

        self.audit.log(
            "liheap_application_serialized",
            member_id,
            {
                "timestamp": datetime.utcnow().isoformat(),
                "bundle_keys": list(serialized_bundle.keys())
            }
        )

        # Stub endpoint for LIHEAP submission
        url = "https://state-benefits.example/api/liheap/submit"

        self.audit.log(
            "liheap_submission_attempt",
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
                    "stage": "liheap_submission",
                    "application": application
                }
            )

        # Store submission result
        self.state.save_member_state(
            member_id,
            {
                "type": "LIHEAP_SUBMISSION",
                "application": application,
                "serialized": serialized_bundle,
                "submission_result": result,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

        self.audit.log(
            "liheap_submission_completed",
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
    engine = LIHEAPSubmissionEngine()

    example_application = {
        "member_id": "M-LIHEAP-001",
        "application_type": "LIHEAP Application",
        "version": "1.0",
        "timestamp": datetime.utcnow().isoformat(),
        "applicant": {
            "first_name": "Laura",
            "last_name": "Benson",
            "date_of_birth": "1985-02-14",
            "ssn_last4": "1234"
        },
        "household": {
            "total_household_members": "1"
        },
        "energy": {
            "heating_provider": "Duke Energy",
            "cooling_provider": "Duke Energy",
            "account_number": "123456789",
            "disconnect_notice": True,
            "crisis": True
        },
        "income": {
            "monthly_gross_income": "0",
            "employment_status": "UNEMPLOYED"
        },
        "signature": {
            "applicant_signature": "Laura Benson",
            "signature_date": datetime.utcnow().isoformat()
        }
    }

    print(engine.submit(example_application))
