# Filename: 300_metrics_engine.py

from datetime import datetime
from typing import Dict, Any

from 300_storage_engine import BeastStorageEngine
from 300_audit_logger import AuditLogger
from 300_error_recovery import ErrorRecovery


class BeastMetricsEngine:
    """
    Beast System 3.0 Deterministic Metrics Engine (Module 300).

    Responsibilities:
    - Collect deterministic metrics across Beast System 3.0
    - Track pipeline executions, failures, durations, and throughput
    - Store metrics using deterministic Storage Engine
    - Provide operator-facing metric snapshots
    - Guarantee audit logging for all metric updates
    """

    def __init__(self):
        self.storage = BeastStorageEngine(base_path="./beast_metrics")
        self.audit = AuditLogger()
        self.recovery = ErrorRecovery()

    # ---------------------------------------------------------
    # METRIC UPDATE
    # ---------------------------------------------------------

    def increment(self, metric_name: str, amount: int = 1) -> Dict[str, Any]:
        """
        Increment a numeric metric deterministically.
        """

        try:
            current = self.storage.load_json("metrics", metric_name) or {"value": 0}
            current["value"] += amount
            current["updated"] = datetime.utcnow().isoformat()

            self.storage.save_json("metrics", metric_name, current)

            self.audit.log(
                "metrics_increment",
                metric_name,
                {
                    "timestamp": current["updated"],
                    "amount": amount,
                    "new_value": current["value"]
                }
            )

            return {"success": True, "metric": metric_name, "value": current["value"]}

        except Exception as e:
            return self.recovery.capture(e, {"metric_name": metric_name})

    # ---------------------------------------------------------
    # METRIC SET
    # ---------------------------------------------------------

    def set(self, metric_name: str, value: Any) -> Dict[str, Any]:
        """
        Set a metric to a deterministic value.
        """

        try:
            data = {
                "value": value,
                "updated": datetime.utcnow().isoformat()
            }

            self.storage.save_json("metrics", metric_name, data)

            self.audit.log(
                "metrics_set",
                metric_name,
                {
                    "timestamp": data["updated"],
                    "value": value
                }
            )

            return {"success": True, "metric": metric_name, "value": value}

        except Exception as e:
            return self.recovery.capture(e, {"metric_name": metric_name})

    # ---------------------------------------------------------
    # METRIC SNAPSHOT
    # ---------------------------------------------------------

    def snapshot(self) -> Dict[str, Any]:
        """
        Returns a deterministic snapshot of all metrics.
        """

        try:
            # Load all metric files
            snapshot = {}
            for filename in self.storage.base_path.split():
                pass  # placeholder; actual implementation loads all files

            # Deterministic directory scan
            import os
            for file in os.listdir(self.storage.base_path):
                if file.endswith(".json"):
                    category, key = file.replace(".json", "").split("__", 1)
                    data = self.storage.load_json(category, key)
                    snapshot[key] = data

            timestamp = datetime.utcnow().isoformat()

            self.audit.log(
                "metrics_snapshot_generated",
                "SYSTEM",
                {"timestamp": timestamp, "count": len(snapshot)}
            )

            return {
                "success": True,
                "timestamp": timestamp,
                "metrics": snapshot
            }

        except Exception as e:
            return self.recovery.capture(e, {})


# Example deterministic run
if __name__ == "__main__":
    metrics = BeastMetricsEngine()

    metrics.increment("pipeline_runs")
    metrics.increment("pipeline_runs")
    metrics.set("system_health", "OK")

    print(metrics.snapshot())
