# Filename: 300_compliance_engine.py

from datetime import datetime
from typing import Dict, Any, List

from 300_audit_logger import AuditLogger
from 300_error_recovery import ErrorRecovery
from 300_security_layer import BeastSecurityLayer


class BeastComplianceEngine:
    """
    Beast System 3.0 Deterministic Compliance Engine (Module 300).

    Responsibilities:
    - Validate compliance across all benefit pipelines
    - Enforce federal, state, and internal policy rules
    - Produce deterministic compliance reports
    - Guarantee audit logging for all compliance checks
    - Provide fallback and recovery on compliance failures
    """

    def __init__(self):
        self.audit = AuditLogger()
        self.recovery = ErrorRecovery()
        self.security = BeastSecurityLayer()

        # Deterministic compliance rule registry
        self.rules = {
            "ssa": [
                "ssa16_required",
                "ssa3368_required",
                "ssa827_required"
            ],
            "va": [
                "va_intake_required"
            ],
            "unemployment": [
                "ui_intake_required"
            ],
            "state": [
                "snap_required",
                "medicaid_required",
                "tanf_required"
            ]
        }

    # ---------------------------------------------------------
    # COMPLIANCE CHECK
    # ---------------------------------------------------------

    def check(self, member_id: str, state_snapshot: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deterministic compliance check across all benefit pipelines.
        """

        timestamp = datetime.utcnow().isoformat()

        missing: List[str] = []

        # SSA compliance
        if not state_snapshot.get("SSA16_INTAKE"):
            missing.append("ssa16_required")
        if not state_snapshot.get("SSA3368_REPORT"):
            missing.append("ssa3368_required")
        if not state_snapshot.get("SSA827_AUTHORIZATION"):
            missing.append("ssa827_required")

        # VA compliance
        if not state_snapshot.get("VA_INTAKE"):
            missing.append("va_intake_required")

        # Unemployment compliance
        if not state_snapshot.get("UNEMPLOYMENT_INTAKE"):
            missing.append("ui_intake_required")

        # State compliance
        if not state_snapshot.get("SNAP_SUBMISSION"):
            missing.append("snap_required")
        if not state_snapshot.get("MEDICAID_SUBMISSION"):
            missing.append("medicaid_required")
        if not state_snapshot.get("TANF_SUBMISSION"):
            missing.append("tanf_required")

        report = {
            "member_id": member_id,
            "timestamp": timestamp,
            "missing_requirements": missing,
            "compliant": len(missing) == 0
        }

        self.audit.log(
            "compliance_check_completed",
            member_id,
            {
                "timestamp": timestamp,
                "missing": missing,
                "compliant": report["compliant"]
            }
        )

        return report

    # ---------------------------------------------------------
    # COMPLIANCE SNAPSHOT
    # ---------------------------------------------------------

    def snapshot(self) -> Dict[str, Any]:
        """
        Returns deterministic compliance rule snapshot.
        """

        timestamp = datetime.utcnow().isoformat()

        snapshot = {
            "timestamp": timestamp,
            "rules": self.rules
        }

        self.audit.log(
            "compliance_snapshot_generated",
            "SYSTEM",
            {"timestamp": timestamp}
        )

        return snapshot


# Example deterministic run
if __name__ == "__main__":
    compliance = BeastComplianceEngine()

    fake_state = {
        "SSA16_INTAKE": True,
        "SSA3368_REPORT": False,
        "SSA827_AUTHORIZATION": True,
        "VA_INTAKE": True,
        "UNEMPLOYMENT_INTAKE": False,
        "SNAP_SUBMISSION": True,
        "MEDICAID_SUBMISSION": False,
        "TANF_SUBMISSION": True
    }

    print(compliance.check("M-TEST-001", fake_state))
    print(compliance.snapshot())
