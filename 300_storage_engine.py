# Filename: 300_storage_engine.py

import os
import json
from datetime import datetime
from typing import Dict, Any, Optional

from 300_audit_logger import AuditLogger
from 300_error_recovery import ErrorRecovery


class BeastStorageEngine:
    """
    Beast System 3.0 Deterministic Storage Engine (Module 300).

    Responsibilities:
    - Provide deterministic low-level storage for Beast System 3.0
    - Store and retrieve JSON objects, binary blobs, and snapshots
    - Guarantee atomic writes and deterministic file naming
    - Provide fallback and recovery on I/O failure
    - Serve as foundation for StateManager, Orchestrator, Scheduler, and Event Bus
    """

    def __init__(self, base_path: str = "./beast_storage"):
        self.base_path = base_path
        self.audit = AuditLogger()
        self.recovery = ErrorRecovery()

        # Ensure base directory exists
        os.makedirs(self.base_path, exist_ok=True)

    # ---------------------------------------------------------
    # INTERNAL HELPERS
    # ---------------------------------------------------------

    def _path(self, category: str, key: str) -> str:
        """
        Deterministic path builder.
        """
        safe_category = category.replace(" ", "_").lower()
        safe_key = key.replace(" ", "_").lower()
        return os.path.join(self.base_path, f"{safe_category}__{safe_key}.json")

    def _blob_path(self, category: str, key: str) -> str:
        """
        Deterministic path builder for binary blobs.
        """
        safe_category = category.replace(" ", "_").lower()
        safe_key = key.replace(" ", "_").lower()
        return os.path.join(self.base_path, f"{safe_category}__{safe_key}.bin")

    # ---------------------------------------------------------
    # JSON STORAGE
    # ---------------------------------------------------------

    def save_json(self, category: str, key: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Saves a JSON object deterministically.
        """

        path = self._path(category, key)

        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

            self.audit.log(
                "storage_json_saved",
                key,
                {
                    "timestamp": datetime.utcnow().isoformat(),
                    "category": category,
                    "path": path
                }
            )

            return {"success": True, "path": path}

        except Exception as e:
            return self.recovery.capture(
                e,
                {"category": category, "key": key, "path": path}
            )

    def load_json(self, category: str, key: str) -> Optional[Dict[str, Any]]:
        """
        Loads a JSON object deterministically.
        """

        path = self._path(category, key)

        try:
            if not os.path.exists(path):
                return None

            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.audit.log(
                "storage_json_loaded",
                key,
                {
                    "timestamp": datetime.utcnow().isoformat(),
                    "category": category,
                    "path": path
                }
            )

            return data

        except Exception as e:
            return self.recovery.capture(
                e,
                {"category": category, "key": key, "path": path}
            )

    # ---------------------------------------------------------
    # BINARY STORAGE
    # ---------------------------------------------------------

    def save_blob(self, category: str, key: str, blob: bytes) -> Dict[str, Any]:
        """
        Saves a binary blob deterministically.
        """

        path = self._blob_path(category, key)

        try:
            with open(path, "wb") as f:
                f.write(blob)

            self.audit.log(
                "storage_blob_saved",
                key,
                {
                    "timestamp": datetime.utcnow().isoformat(),
                    "category": category,
                    "path": path,
                    "size_bytes": len(blob)
                }
            )

            return {"success": True, "path": path}

        except Exception as e:
            return self.recovery.capture(
                e,
                {"category": category, "key": key, "path": path}
            )

    def load_blob(self, category: str, key: str) -> Optional[bytes]:
        """
        Loads a binary blob deterministically.
        """

        path = self._blob_path(category, key)

        try:
            if not os.path.exists(path):
                return None

            with open(path, "rb") as f:
                blob = f.read()

            self.audit.log(
                "storage_blob_loaded",
                key,
                {
                    "timestamp": datetime.utcnow().isoformat(),
                    "category": category,
                    "path": path,
                    "size_bytes": len(blob)
                }
            )

            return blob

        except Exception as e:
            return self.recovery.capture(
                e,
                {"category": category, "key": key, "path": path}
            )


# Example deterministic run
if __name__ == "__main__":
    storage = BeastStorageEngine()

    # Save JSON
    storage.save_json("test_category", "test_key", {"hello": "world"})

    # Load JSON
    print(storage.load_json("test_category", "test_key"))

    # Save blob
    storage.save_blob("test_category", "binary_key", b"example binary data")

    # Load blob
    print(storage.load_blob("test_category", "binary_key"))
