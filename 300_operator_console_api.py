# Filename: 300_operator_console_api.py

from datetime import datetime
from typing import Dict, Any

from 300_master_orchestrator import BeastMasterOrchestrator
from 300_federal_sync_engine import FederalSyncEngine
from 300_event_bus import BeastEventBus
from 300_scheduler import BeastScheduler
from 300_state_manager import StateManager
from 300_audit_logger import AuditLogger
from 300_error_recovery import ErrorRecovery


class OperatorConsoleAPI:
    """
    Beast System 3.0 Operator Console API (Module 300).

    Responsibilities:
    - Provide deterministic external interface for operators
    - Expose orchestrator controls
    - Expose scheduler controls
    - Expose event bus publishing
    - Expose state inspection and audit inspection
    - Guarantee safe, validated, logged interactions
    """

    def __init__(self):
        self.orchestrator = BeastMasterOrchestrator()
        self.sync = FederalSyncEngine()
        self.bus = BeastEventBus()
        self.scheduler = BeastScheduler()
        self.state = StateManager()
        self.audit = AuditLogger()
        self.recovery = ErrorRecovery()

    # ---------------------------------------------------------
    # ORCHESTRATOR CONTROL
    # ---------------------------------------------------------

    def run_full_pipeline(self, member_id: str) -> Dict[str, Any]:
        """
        Operator-triggered full pipeline execution.
        """

        self.audit.log(
            "operator_api_run_full_pipeline",
            member_id,
            {"timestamp": datetime.utcnow().isoformat()}
        )

        try:
            return self.orchestrator.run_full_pipeline(member_id)
        except Exception as e:
            return self.recovery.capture(e, {"member_id": member_id})

    # ---------------------------------------------------------
    # FEDERAL SYNC CONTROL
    # ---------------------------------------------------------

    def run_federal_sync(self, member_id: str) -> Dict[str, Any]:
        """
        Operator-triggered federal sync.
        """

        self.audit.log(
            "operator_api_run_federal_sync",
            member_id,
            {"timestamp": datetime.utcnow().isoformat()}
        )

        try:
            return self.sync.sync(member_id)
        except Exception as e:
            return self.recovery.capture(e, {"member_id": member_id})

    # ---------------------------------------------------------
    # EVENT BUS CONTROL
    # ---------------------------------------------------------

    def publish_event(self, event_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Operator-triggered event publishing.
        """

        self.audit.log(
            "operator_api_publish_event",
            payload.get("member_id", "SYSTEM"),
            {
                "timestamp": datetime.utcnow().isoformat(),
                "event_name": event_name
            }
        )

        try:
            self.bus.publish(event_name, payload)
            return {"success": True, "event": event_name, "payload": payload}
        except Exception as e:
            return self.recovery.capture(e, {"event_name": event_name, "payload": payload})

    # ---------------------------------------------------------
    # SCHEDULER CONTROL
    # ---------------------------------------------------------

    def run_scheduler_cycle(self) -> Dict[str, Any]:
        """
        Operator-triggered scheduler cycle.
        """

        self.audit.log(
            "operator_api_run_scheduler_cycle",
            "SYSTEM",
            {"timestamp": datetime.utcnow().isoformat()}
        )

        try:
            self.scheduler.run_due_tasks()
            return {"success": True, "tasks": self.scheduler.list_tasks()}
        except Exception as e:
            return self.recovery.capture(e, {})

    # ---------------------------------------------------------
    # STATE INSPECTION
    # ---------------------------------------------------------

    def inspect_state(self, member_id: str) -> Dict[str, Any]:
        """
        Operator-triggered state inspection.
        """

        self.audit.log(
            "operator_api_inspect_state",
            member_id,
            {"timestamp": datetime.utcnow().isoformat()}
        )

        try:
            return self.state.get_all_states(member_id)
        except Exception as e:
            return self.recovery.capture(e, {"member_id": member_id})

    # ---------------------------------------------------------
    # AUDIT INSPECTION
    # ---------------------------------------------------------

    def inspect_audit(self, member_id: str) -> Dict[str, Any]:
        """
        Operator-triggered audit inspection.
        """

        self.audit.log(
            "operator_api_inspect_audit",
            member_id,
            {"timestamp": datetime.utcnow().isoformat()}
        )

        try:
            return self.audit.get_logs(member_id)
        except Exception as e:
            return self.recovery.capture(e, {"member_id": member_id})


# Example deterministic run
if __name__ == "__main__":
    api = OperatorConsoleAPI()

    print(api.run_full_pipeline("M-TEST-001"))
    print(api.run_federal_sync("M-TEST-001"))
    print(api.publish_event("TEST_EVENT", {"member_id": "M-TEST-001", "msg": "Hello"}))
    print(api.run_scheduler_cycle())
    print(api.inspect_state("M-TEST-001"))
    print(api.inspect_audit("M-TEST-001"))
