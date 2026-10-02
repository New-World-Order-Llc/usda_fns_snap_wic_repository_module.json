# Filename: 300_event_bus.py

from datetime import datetime
from typing import Dict, Any, Callable, List

from 300_audit_logger import AuditLogger
from 300_error_recovery import ErrorRecovery


class BeastEventBus:
    """
    Beast System 3.0 Deterministic Event Bus (Module 300).

    Responsibilities:
    - Provide deterministic internal messaging between modules
    - Support event publishing and subscription
    - Guarantee ordered, auditable event flow
    - Provide fallback and recovery on handler failure
    - Serve as backbone for orchestrator, sync engine, and benefit modules
    """

    def __init__(self):
        self.audit = AuditLogger()
        self.recovery = ErrorRecovery()

        # Event registry: event_name -> list of handlers
        self._handlers: Dict[str, List[Callable[[Dict[str, Any]], None]]] = {}

    def subscribe(self, event_name: str, handler: Callable[[Dict[str, Any]], None]):
        """
        Registers a handler for a specific event.
        """

        if event_name not in self._handlers:
            self._handlers[event_name] = []

        self._handlers[event_name].append(handler)

        self.audit.log(
            "event_bus_subscription_added",
            "SYSTEM",
            {
                "timestamp": datetime.utcnow().isoformat(),
                "event_name": event_name,
                "handler": handler.__name__
            }
        )

    def publish(self, event_name: str, payload: Dict[str, Any]):
        """
        Publishes an event to all registered handlers.
        """

        timestamp = datetime.utcnow().isoformat()

        self.audit.log(
            "event_bus_event_published",
            payload.get("member_id", "SYSTEM"),
            {
                "timestamp": timestamp,
                "event_name": event_name,
                "payload_keys": list(payload.keys())
            }
        )

        handlers = self._handlers.get(event_name, [])

        for handler in handlers:
            try:
                handler(payload)
            except Exception as e:
                self.recovery.capture(
                    e,
                    {
                        "event_name": event_name,
                        "handler": handler.__name__,
                        "payload": payload
                    }
                )

                self.audit.log(
                    "event_bus_handler_failure",
                    payload.get("member_id", "SYSTEM"),
                    {
                        "timestamp": datetime.utcnow().isoformat(),
                        "event_name": event_name,
                        "handler": handler.__name__,
                        "error": str(e)
                    }
                )

    def list_handlers(self) -> Dict[str, List[str]]:
        """
        Returns a deterministic list of registered handlers.
        """

        return {
            event: [h.__name__ for h in handlers]
            for event, handlers in self._handlers.items()
        }


# Example deterministic run
if __name__ == "__main__":
    bus = BeastEventBus()

    def example_handler(payload):
        print("Handled event:", payload)

    bus.subscribe("TEST_EVENT", example_handler)
    bus.publish("TEST_EVENT", {"member_id": "M-TEST-001", "data": "Hello"})
    print(bus.list_handlers())
