from collections import deque
import json
from datetime import datetime


class ShortTermMemory:
    def __init__(self, max_size: int = 50):
        self.max_size = max_size
        self.entries = deque(maxlen=max_size)

    def add(self, entry: dict):
        entry["timestamp"] = entry.get("timestamp", datetime.now().isoformat())
        self.entries.append(entry)

    def get_recent(self, count: int = 10) -> list[dict]:
        return list(self.entries)[-count:]

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        query_lower = query.lower()
        scored = []
        for entry in self.entries:
            text = json.dumps(entry).lower()
            score = text.count(query_lower) / max(len(text), 1)
            if score > 0:
                scored.append({"score": score, **entry})
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]

    def clear(self):
        self.entries.clear()

    def get_all(self) -> list[dict]:
        return list(self.entries)
