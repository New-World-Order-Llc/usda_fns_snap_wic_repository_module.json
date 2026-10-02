# Filename: 300_unemployment_weekly_certification.py

from datetime import datetime
from typing import Dict, Any

from 300_state_manager import StateManager
from 300_network_adapter import NetworkAdapter
from 300_audit_logger import AuditLogger
from 300_error_recovery import ErrorRecovery
from 300_data_serialization import DataSerializationEngine


class UnemploymentWeeklyCertificationEngine:
    """
    Deterministic Weekly Certification Engine for Beast System 3.0 (Module 300).

    Supports:
    - Weekly unemployment eligibility certification
    - Work search reporting
    - Earnings reporting
    - Availability for work attestation

    Responsibilities:
    - Accept weekly claimant data
    - Build deterministic weekly certification payload
    - Serialize and store in StateManager
    - Submit via NetworkAdapter (stub endpoint)
    - Log all events in AuditLogger
    - Provide deterministic fallback on failure
    """

    def __init__(self):
        self.state = StateManager()
        self.network = NetworkAdapter()
        self.audit = AuditLogger()
        self.recovery = ErrorRecovery()
        self.serializer = DataSerializationEngine()

    def build_certification(self, member_id: str, weekly_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Builds a deterministic weekly certification payload.
        """

        payload = {
            "member_id": member_id,
            "certification_type": "UNEMPLOYMENT_WEEKLY_CERTIFICATION",
            "version": "1.0",
            "timestamp": datetime.utcnow().isoformat(),
            "week_ending": weekly_data.get("week_ending", ""),
            "earnings": weekly_data.get("earnings", "0"),
            "work_search": weekly_data.get("work_search", []),
            "availability": weekly_data.get("availability", True),
            "refusals": weekly_data.get("refusals", []),
            "signature": {
                "claimant_signature": "",
                "signature_date": ""
            }
        }

        serialized = self.serializer.serialize_pipeline_result(payload)

        self.state.save_member_state(
            member_id,
            {
                "type": "UNEMPLOYMENT_WEEKLY_CERTIFICATION",
                "data": payload,
                "serialized": serialized,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

        self.audit.log(
            "unemployment_weekly_certification_built",
            member_id,
            {"timestamp": payload["timestamp"]}
        )

        return {
            "success": True,
            "member_id": member_id,
            "payload": payload,
            "serialized_bundle": serialized
        }

    def submit(self, member_id: str) -> Dict[str, Any]:
        """
        Submits the weekly certification.
        """

        stored = self.state.get_member_state(member_id, "UNEMPLOYMENT_WEEKLY_CERTIFICATION")

        if not stored:
            self.audit.log(
                "unemployment_weekly_certification_missing",
                member_id,
                {"error": "No weekly certification found"}
            )
            return {
                "success": False,
                "member_id": member_id,
                "error": "No weekly certification found"
            }

        payload = stored["data"]
        serialized = stored["serialized"]

        url = "https://state-benefits.example/api/unemployment/certify"

        self.audit.log(
            "unemployment_weekly_certification_submission_attempt",
            member_id,
            {"url": url}
        )

        try:
            result = self.network._request(url, payload)
        except Exception as e:
            result = self.recovery.capture(
                e,
                {
                    "member_id": member_id,
                    "stage": "unemployment_weekly_certification_submission",
                    "payload": payload
                }
            )

        self.state.save_member_state(
            member_id,
            {
                "type": "UNEMPLOYMENT_WEEKLY_CERTIFICATION_SUBMISSION",
                "payload": payload,
                "serialized": serialized,
                "submission_result": result,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

        self.audit.log(
            "unemployment_weekly_certification_submission_completed",
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
            "serialized_bundle": serialized
        }


# Example deterministic run
if __name__ == "__main__":
    engine = UnemploymentWeeklyCertificationEngine()

    weekly_data = {
        "week_ending": "2024-07-12",
        "earnings": "0",
        "work_search": [
            {"employer": "Local Store", "method": "Online", "date": "2024-07-08"},
            {"employer": "Warehouse Co", "method": "In-person", "date": "2024-07-09"}
        ],
        "availability": True,
        "refusals": []
    }

    built = engine.build_certification("M-UI-001", weekly_data)
    print(built)

    print(engine.submit("M-UI-001"))
