# Filename: 300_master_orchestrator.py

from datetime import datetime
from typing import Dict, Any

from 300_audit_logger import AuditLogger
from 300_error_recovery import ErrorRecovery
from 300_state_manager import StateManager
from 300_federal_sync_engine import FederalSyncEngine

# Benefit engines
from 300_snap_submission import SNAPSubmissionEngine
from 300_medicaid_submission import MedicaidSubmissionEngine
from 300_tanf_submission import TANFSubmissionEngine
from 300_housing_submission import HousingSubmissionEngine
from 300_liheap_submission import LIHEAPSubmissionEngine
from 300_childcare_submission import ChildcareSubmissionEngine

# Federal engines
from 300_ssa_submission import SSASubmissionEngine
from 300_va_submission import VASubmissionEngine
from 300_unemployment_weekly_certification import UnemploymentWeeklyCertificationEngine


class BeastMasterOrchestrator:
    """
    Beast System 3.0 Master Orchestrator (Module 300).

    Responsibilities:
    - Coordinate all benefit pipelines
    - Execute deterministic multi-program submissions
    - Trigger federal sync after state-level operations
    - Provide unified execution logs
    - Handle fallback and recovery
    """

    def __init__(self):
        self.audit = AuditLogger()
        self.recovery = ErrorRecovery()
        self.state = StateManager()

        # State-level engines
        self.snap = SNAPSubmissionEngine()
        self.medicaid = MedicaidSubmissionEngine()
        self.tanf = TANFSubmissionEngine()
        self.housing = HousingSubmissionEngine()
        self.liheap = LIHEAPSubmissionEngine()
        self.childcare = ChildcareSubmissionEngine()

        # Federal engines
        self.ssa = SSASubmissionEngine()
        self.va = VASubmissionEngine()
        self.ui_weekly = UnemploymentWeeklyCertificationEngine()

        # Sync engine
        self.federal_sync = FederalSyncEngine()

    def run_full_pipeline(self, member_id: str) -> Dict[str, Any]:
        """
        Executes the full Beast System 3.0 pipeline for a member.
        """

        self.audit.log(
            "master_orchestrator_start",
            member_id,
            {"timestamp": datetime.utcnow().isoformat()}
        )

        results = {}

        try:
            # State-level submissions
            results["snap"] = self.snap.submit(member_id)
            results["medicaid"] = self.medicaid.submit({"member_id": member_id})
            results["tanf"] = self.tanf.submit({"member_id": member_id})
            results["housing"] = self.housing.submit({"member_id": member_id})
            results["liheap"] = self.liheap.submit({"member_id": member_id})
            results["childcare"] = self.childcare.submit({"member_id": member_id})

            # Federal submissions
            results["ssa"] = self.ssa.submit(member_id)
            results["va"] = self.va.submit(member_id)

            # Unemployment weekly certification (if present)
            results["unemployment_weekly"] = self.ui_weekly.submit(member_id)

            # Federal sync
            results["federal_sync"] = self.federal_sync.sync(member_id)

        except Exception as e:
            recovery = self.recovery.capture(
                e,
                {
                    "member_id": member_id,
                    "stage": "master_orchestrator"
                }
            )

            self.audit.log(
                "master_orchestrator_failure",
                member_id,
                {"error": str(e)}
            )

            return {
                "success": False,
                "member_id": member_id,
                "error": str(e),
                "recovery": recovery
            }

        self.audit.log(
            "master_orchestrator_complete",
            member_id,
            {
                "timestamp": datetime.utcnow().isoformat(),
                "components_executed": list(results.keys())
            }
        )

        return {
            "success": True,
            "member_id": member_id,
            "results": results
        }


# Example deterministic run
if __name__ == "__main__":
    orchestrator = BeastMasterOrchestrator()
    print(orchestrator.run_full_pipeline("M-TEST-001"))
