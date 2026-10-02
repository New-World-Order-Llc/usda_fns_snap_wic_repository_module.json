# Filename: 300_va_submission.py

from datetime import datetime
from typing import Dict, Any

from 300_state_manager import StateManager
from 300_network_adapter import NetworkAdapter
from 300_audit_logger import AuditLogger
from 300_error_recovery import ErrorRecovery
from 300_data_serialization import DataSerializationEngine


class VASubmissionEngine:
    """
    Deterministic VA Unified Submission Engine for Beast System 3.0 (Module 300).

    Responsibilities:
    - Retrieve VA intake packet from StateManager
    - Combine service, medical, and functional data into unified submission
    - Serialize deterministically
    - Submit via NetworkAdapter (stub endpoint)
    - Store submission result
    - Log all events
    - Provide deterministic fallback on failure
    """

    def __init__(self):
        self.state = StateManager()
        self.network = NetworkAdapter()
        self.audit = AuditLogger()
        self.recovery = ErrorRecovery()
        self.serializer = DataSerializationEngine()

    def build_packet(self, member_id: str) -> Dict[str, Any]:
        """
        Builds a unified VA disability submission packet.
        """

        va_intake = self.state.get_member_state(member_id, "VA_INTAKE")

        if not va_intake:
            self.audit.log(
                "va_submission_missing_intake",
                member_id,
                {"missing": ["VA_INTAKE"]}
            )
            return {
                "success": False,
                "member_id": member_id,
                "error": "Missing VA intake data",
                "missing": ["VA_INTAKE"]
            }

        packet = {
            "member_id": member_id,
            "submission_type": "VA_DISABILITY_FULL_SUBMISSION",
            "version": "1.0",
            "timestamp": datetime.utcnow().isoformat(),
            "components": {
                "va_intake": va_intake["data"]
            }
        }

        self.audit.log(
            "va_submission_packet_built",
            member_id,
            {"timestamp": packet["timestamp"]}
        )

        return {
            "success": True,
            "packet": packet
        }

    def submit(self, member_id: str) -> Dict[str, Any]:
        """
        Submits the unified VA disability packet.
        """

        packet_result = self.build_packet(member_id)
        if not packet_result["success"]:
            return packet_result

        packet = packet_result["packet"]

        serialized = self.serializer.serialize_pipeline_result(packet)

        self.audit.log(
            "va_submission_serialized",
            member_id,
            {"timestamp": datetime.utcnow().isoformat()}
        )

        url = "https://va.gov/api/disability/submit"

        self.audit.log(
            "va_submission_attempt",
            member_id,
            {"url": url}
        )

        try:
            result = self.network._request(url, packet)
        except Exception as e:
            result = self.recovery.capture(
                e,
                {
                    "member_id": member_id,
                    "stage": "va_submission",
                    "packet": packet
                }
            )

        self.state.save_member_state(
            member_id,
            {
                "type": "VA_FULL_SUBMISSION",
                "packet": packet,
                "serialized": serialized,
                "submission_result": result,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

        self.audit.log(
            "va_submission_completed",
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
    engine = VASubmissionEngine()
    print(engine.submit("M-VA-001"))
