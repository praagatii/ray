import json
import os
import copy

STORAGE_DIR = os.path.join(os.path.dirname(__file__), "storage")
STORAGE_PATH = os.path.join(STORAGE_DIR, "identity.json")

DEFAULT_IDENTITY = {
    "name": "",
    "goals": [],
    "projects": [],
    "preferences": [],
    "working_style": {},
    "facts": []
}


class IdentityMemory:
    def __init__(self):
        os.makedirs(STORAGE_DIR, exist_ok=True)
        if not os.path.exists(STORAGE_PATH):
            self._write(DEFAULT_IDENTITY)

    def _read(self) -> dict:
        with open(STORAGE_PATH, "r") as f:
            return json.load(f)

    def _write(self, data: dict):
        with open(STORAGE_PATH, "w") as f:
            json.dump(data, f, indent=2)

    def update(self, section: str, value):
        data = self._read()
        if section in data:
            existing = data[section]
            if isinstance(existing, list):
                if value not in existing:
                    existing.append(value)
            elif isinstance(existing, dict):
                if isinstance(value, dict):
                    existing.update(value)
            else:
                data[section] = value
        self._write(data)

    def get_identity(self) -> dict:
        return copy.deepcopy(self._read())
