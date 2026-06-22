import json
import os
import uuid
from datetime import datetime, timezone

STORAGE_DIR = os.path.join(os.path.dirname(__file__), "storage")
STORAGE_PATH = os.path.join(STORAGE_DIR, "short_term.json")


class ShortTermMemory:
    def __init__(self):
        os.makedirs(STORAGE_DIR, exist_ok=True)
        if not os.path.exists(STORAGE_PATH):
            self._write([])

    def _read(self) -> list:
        with open(STORAGE_PATH, "r") as f:
            return json.load(f)

    def _write(self, data: list):
        with open(STORAGE_PATH, "w") as f:
            json.dump(data, f, indent=2)

    def add(self, message: str) -> dict:
        entry = {
            "id": str(uuid.uuid4()),
            "text": message,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        data = self._read()
        data.append(entry)
        self._write(data)
        return entry

    def get_recent(self, limit: int = 10) -> list[dict]:
        data = self._read()
        return data[-limit:]

    def clear(self):
        self._write([])
