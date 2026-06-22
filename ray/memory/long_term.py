import json
import os
import uuid
from datetime import datetime, timezone

STORAGE_DIR = os.path.join(os.path.dirname(__file__), "storage")
STORAGE_PATH = os.path.join(STORAGE_DIR, "long_term.json")

RELATED_WORDS = {
    "clients": ["business", "sales", "customer", "revenue", "mugen"],
    "business": ["clients", "sales", "revenue", "company", "startup"],
    "website": ["web", "site", "online", "digital", "mugen"],
    "studio": ["creative", "agency", "mugen"],
    "money": ["clients", "revenue", "business", "sales"],
    "help": ["assistant", "support", "aid"],
    "code": ["programming", "software", "app", "ray"],
    "app": ["software", "code", "programming", "ai", "ray"],
    "ai": ["assistant", "intelligence", "ray", "brain", "software"],
}


class LongTermMemory:
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

    def add_memory(self, memory: dict) -> dict:
        entry = {
            "id": memory.get("id", str(uuid.uuid4())),
            "type": memory.get("type", "general"),
            "content": memory.get("content", ""),
            "created_at": memory.get("created_at", datetime.now(timezone.utc).isoformat()),
            "importance": memory.get("importance", 5),
            "tags": memory.get("tags", [])
        }

        data = self._read()
        merged = self._dedup_and_merge(entry, data)
        if merged is None:
            data.append(entry)
        else:
            for i, m in enumerate(data):
                if m["id"] == merged["id"]:
                    data[i] = merged
                    break

        self._write(data)
        return merged or entry

    def _dedup_and_merge(self, new: dict, existing: list) -> dict | None:
        new_words = set(w for w in new["content"].lower().split() if len(w) > 3)

        for mem in existing:
            mem_words = set(w for w in mem["content"].lower().split() if len(w) > 3)
            if not new_words or not mem_words:
                continue
            overlap = new_words & mem_words
            shorter = min(len(new_words), len(mem_words))
            if shorter > 0 and len(overlap) / shorter >= 0.5:
                merged = dict(mem)
                merged["importance"] = max(mem["importance"], new["importance"])
                merged["tags"] = list(set(mem["tags"] + new["tags"]))[:8]
                merged["created_at"] = datetime.now(timezone.utc).isoformat()
                return merged
        return None

    def search(self, query: str) -> list[dict]:
        data = self._read()
        raw_q = query.lower().strip()
        terms = [t for t in raw_q.split() if len(t) > 2]
        if not terms:
            terms = [raw_q]

        scored = []

        for mem in data:
            total = 0
            reasons = set()
            content_lower = mem["content"].lower()
            tags_lower = [t.lower() for t in mem["tags"]]
            content_words = content_lower.split()

            for term in terms:
                if term in content_lower:
                    total += 10
                    reasons.add("content match")
                if term in tags_lower:
                    total += 8
                    reasons.add("tag match")
                if term in content_words:
                    total += 3
                if any(term in tag for tag in tags_lower):
                    if term not in tags_lower:
                        total += 5
                        reasons.add("partial tag")
                if term in RELATED_WORDS:
                    related = RELATED_WORDS[term]
                    if any(rel in content_lower for rel in related):
                        total += 5
                        reasons.add("related word")
                    if any(rel in tags_lower for rel in related):
                        total += 5
                        reasons.add("related tag")

            if total > 0:
                total += mem["importance"]
                reasons.add(f"imp={mem['importance']}")
                scored.append({
                    "memory": mem,
                    "score": total,
                    "reason": "; ".join(sorted(reasons))
                })

        scored.sort(key=lambda r: r["score"], reverse=True)
        return scored

    def get_all(self) -> list[dict]:
        return self._read()

    def clear(self):
        self._write([])
