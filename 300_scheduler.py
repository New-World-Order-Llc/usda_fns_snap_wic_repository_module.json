# Filename: 300_scheduler.py

from datetime import datetime, timedelta
from typing import Dict, Any, Callable, List

from 300_audit_logger import AuditLogger
from 300_error_recovery import ErrorRecovery


class BeastScheduler:
    """
    Beast System 3.0 Deterministic Scheduler (Module 300).

    Responsibilities:
    - Register timed tasks (interval-based or specific timestamps)
    - Execute tasks deterministically in chronological order
    - Guarantee audit logging for every scheduled run
    - Provide fallback and recovery on task failure
    - Integrate with Event Bus and Master Orchestrator
    """

    def __init__(self):
        self.audit = AuditLogger()
        self.recovery = ErrorRecovery()

        # Internal registry of scheduled tasks
        # Each entry: { "name": str, "handler": callable, "next_run": datetime, "interval": timedelta or None }
        self._tasks: List[Dict[str, Any]] = []

    def schedule_interval(self, name: str, handler: Callable[[], None], interval_seconds: int):
        """
        Schedules a task to run repeatedly at fixed intervals.
        """

        task = {
            "name": name,
            "handler": handler,
            "next_run": datetime.utcnow() + timedelta(seconds=interval_seconds),
            "interval": timedelta(seconds=interval_seconds)
        }

        self._tasks.append(task)

        self.audit.log(
            "scheduler_interval_task_added",
            "SYSTEM",
            {
                "timestamp": datetime.utcnow().isoformat(),
                "task_name": name,
                "interval_seconds": interval_seconds
            }
        )

    def schedule_once(self, name: str, handler: Callable[[], None], run_at: datetime):
        """
        Schedules a one-time task.
        """

        task = {
            "name": name,
            "handler": handler,
            "next_run": run_at,
            "interval": None
        }

        self._tasks.append(task)

        self.audit.log(
            "scheduler_one_time_task_added",
            "SYSTEM",
            {
                "timestamp": datetime.utcnow().isoformat(),
                "task_name": name,
                "run_at": run_at.isoformat()
            }
        )

    def run_due_tasks(self):
        """
        Executes all tasks whose next_run time has passed.
        Deterministic ordering: earliest next_run executes first.
        """

        now = datetime.utcnow()

        # Sort tasks by next_run time
        self._tasks.sort(key=lambda t: t["next_run"])

        for task in list(self._tasks):
            if task["next_run"] <= now:
                self.audit.log(
                    "scheduler_task_execution_start",
                    "SYSTEM",
                    {
                        "timestamp": now.isoformat(),
                        "task_name": task["name"]
                    }
                )

                try:
                    task["handler"]()
                except Exception as e:
                    self.recovery.capture(
                        e,
                        {
                            "task_name": task["name"],
                            "stage": "scheduler_task_execution"
                        }
                    )

                    self.audit.log(
                        "scheduler_task_execution_failure",
                        "SYSTEM",
                        {
                            "timestamp": datetime.utcnow().isoformat(),
                            "task_name": task["name"],
                            "error": str(e)
                        }
                    )

                # Reschedule or remove
                if task["interval"] is not None:
                    # Interval task: schedule next run
                    task["next_run"] = now + task["interval"]
                else:
                    # One-time task: remove
                    self._tasks.remove(task)

                self.audit.log(
                    "scheduler_task_execution_complete",
                    "SYSTEM",
                    {
                        "timestamp": datetime.utcnow().isoformat(),
                        "task_name": task["name"]
                    }
                )

    def list_tasks(self) -> List[Dict[str, Any]]:
        """
        Returns a deterministic list of scheduled tasks.
        """

        return [
            {
                "name": t["name"],
                "next_run": t["next_run"].isoformat(),
                "interval_seconds": t["interval"].total_seconds() if t["interval"] else None
            }
            for t in self._tasks
        ]


# Example deterministic run
if __name__ == "__main__":
    scheduler = BeastScheduler()

    def example_task():
        print("Example task executed at", datetime.utcnow().isoformat())

    scheduler.schedule_interval("heartbeat", example_task, interval_seconds=5)

    scheduler.schedule_once(
        "one_time_sync",
        example_task,
        run_at=datetime.utcnow() + timedelta(seconds=3)
    )

    # Simulate scheduler loop
    for _ in range(10):
        scheduler.run_due_tasks()
