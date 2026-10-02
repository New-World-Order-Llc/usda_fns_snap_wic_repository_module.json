# Filename: 300_benefits_dashboard.py

from datetime import datetime
from typing import Dict, Any

from 300_state_manager import StateManager
from 300_audit_logger import AuditLogger


class BenefitsDashboard:
    """
    Deterministic Universal Benefits Dashboard for Beast System 3.0 (Module 300).

    Responsibilities:
    - Aggregate all benefit program states for a member
    - Provide a unified snapshot
    - Display current status of:
        SNAP
        Medicaid
        TANF
        Housing Assistance
        LIHEAP (Energy Assistance)
        Childcare Assistance
    - Log dashboard views in AuditLogger
    """

    def __init__(self):
        self.state = StateManager()
        self.audit = AuditLogger()

    def snapshot(self, member_id: str) -> Dict[str, Any]:
        """
        Returns a deterministic snapshot of all benefit systems for a member.
        """

        stored = self.state.get_member_state(member_id)

        # If no state exists, return empty dashboard
        if not stored:
            snapshot = {
                "member_id": member_id,
                "timestamp": datetime.utcnow().isoformat(),
                "programs": {},
                "note": "No benefit records found for this member."
            }

            self.audit.log(
                "benefits_dashboard_empty",
                member_id,
                {"timestamp": snapshot["timestamp"]}
            )

            return snapshot

        # Build dashboard
        dashboard = {
            "member_id": member_id,
            "timestamp": datetime.utcnow().isoformat(),
            "programs": {
                "SNAP_APPLICATION": None,
                "SNAP_SUBMISSION": None,
                "SNAP_STATUS": None,
                "SNAP_RENEWAL": None,
                "MEDICAID_SUBMISSION": None,
                "TANF_SUBMISSION": None,
                "HOUSING_SUBMISSION": None,
                "LIHEAP_SUBMISSION": None,
                "CHILDCARE_SUBMISSION": None
            }
        }

        # Populate dashboard with stored program states
        for key in dashboard["programs"].keys():
            if stored["data"].get("type") == key:
                dashboard["programs"][key] = stored["data"]

        self.audit.log(
            "benefits_dashboard_viewed",
            member_id,
            {
                "timestamp": dashboard["timestamp"],
                "programs_found": [
                    k for k, v in dashboard["programs"].items() if v is not None
                ]
            }
        )

        return dashboard


# Example deterministic run
if __name__ == "__main__":
    dashboard = BenefitsDashboard()
    print(dashboard.snapshot("M-SNAP-001"))
