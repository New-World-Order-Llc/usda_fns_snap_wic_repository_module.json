# Filename: 300_ssa_submission.py

from datetime import datetime
from typing import Dict, Any

from 300_state_manager import StateManager
from 300_network_adapter import NetworkAdapter
from 300_audit_logger import AuditLogger
from 300_error_recovery import ErrorRecovery
from 300_data_serialization import DataSerializationEngine


class SSASubmissionEngine:
    """
    Deterministic SSA Unified Submission Engine for Beast System 3.0 (Module 300).

    Responsibilities:
    - Retrieve SSA-16, SSA-3368, SSA-827 from StateManager
    - Combine into a unified SSA disability submission packet
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
        Builds a unified SSA disability submission packet.
        """

        ssa16 = self.state.get_member_state(member_id, "SSA16_INTAKE")
        ssa3368 = self.state.get_member_state(member_id, "SSA3368_REPORT")
        ssa827 = self.state.get_member_state(member_id, "SSA827_AUTHORIZATION")

        missing = []
        if not ssa16: missing.append("SSA16_INTAKE")
        if not ssa3368: missing.append("SSA3368_REPORT")
        if not ssa827: missing.append("SSA827_AUTHORIZATION")

        if missing:
            self.audit.log(
                "ssa_submission_missing_components",
                member_id,
                {"missing": missing}
            )
            return {
                "success": False,
                "member_id": member_id,
                "error": "Missing required SSA components",
                "missing": missing
            }

        packet = {
            "member_id": member_id,
            "submission_type": "SSA_DISABILITY_FULL_SUBMISSION",
            "version": "1.0",
            "timestamp": datetime.utcnow().isoformat(),
            "components": {
                "ssa16": ssa16["data"],
                "ssa3368": ssa3368["data"],
                "ssa827": ssa827["data"]
            }
        }

        self.audit.log(
            "ssa_submission_packet_built",
            member_id,
            {"timestamp": packet["timestamp"]}
        )

        return {
            "success": True,
            "packet": packet
        }

    def submit(self, member_id: str) -> Dict[str, Any]:
        """
        Submits the unified SSA disability packet.
        """

        packet_result = self.build_packet(member_id)
        if not packet_result["success"]:
            return packet_result

        packet = packet_result["packet"]

        serialized = self.serializer.serialize_pipeline_result(packet)

        self.audit.log(
            "ssa_submission_serialized",
            member_id,
            {"timestamp": datetime.utcnow().isoformat()}
        )

        url = "https://ssa.gov/api/disability/submit"

        self.audit.log(
            "ssa_submission_attempt",
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
                    "stage": "ssa_submission",
                    "packet": packet
                }
            )

        self.state.save_member_state(
            member_id,
            {
                "type": "SSA_FULL_SUBMISSION",
                "packet": packet,
                "serialized": serialized,
                "submission_result": result,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

        self.audit.log(
            "ssa_submission_completed",
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
    engine = SSASubmissionEngine()
    print(engine.submit("M-SSA-001"))
