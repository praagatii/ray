import re
from ray.memory.long_term import LongTermMemory

GREETINGS = {"hi", "hello", "hey", "yo", "sup", "good morning", "good evening"}


class ReflectionEngine:
    def __init__(self):
        self.ltm = LongTermMemory()

    def reflect(self, interaction: dict) -> dict:
        msg = interaction.get("user_message", "").strip().lower()
        memories = []

        if self._is_noise(msg):
            return {"should_remember": False, "memories": []}

        patterns = [
            (r"(?:i\s+)?want\s+(.+?)(?:\.|$)", "goal"),
            (r"(?:i'?m?\s*)?(?:building?|working\s+on|making?|creating?|developing?)\s+(.+?)(?:\.|$)", "project"),
            (r"i\s+(?:hate|love|enjoy|prefer|don't\s+like|can't\s+stand)\s+(.+?)(?:\.|$)", "preference"),
            (r"i\s+(?:struggle|feel\s+stuck|have\s+trouble|find\s+it\s+hard)\s+(?:with\s+)?(.+?)(?:\.|$)", "problem"),
        ]

        for pattern, mem_type in patterns:
            match = re.search(pattern, msg)
            if match:
                raw = match.group(1).strip()
                if len(raw) > 3:
                    content = self._clean_content(raw, msg, mem_type)
                    memories.append({
                        "type": mem_type,
                        "content": content,
                        "importance": self._importance(mem_type),
                        "tags": self._tags(content, mem_type)
                    })

        has_existing = any(
            m["content"] in [e["content"] for e in self.ltm.get_all()]
            for m in memories
        )

        return {
            "should_remember": len(memories) > 0 and not has_existing,
            "memories": memories
        }

    def store(self, result: dict):
        if not result["should_remember"]:
            return
        for mem in result["memories"]:
            self.ltm.add_memory(mem)

    def _is_noise(self, msg: str) -> bool:
        if msg in GREETINGS:
            return True
        if len(msg.split()) <= 2:
            return True
        return False

    def _importance(self, mem_type: str) -> int:
        return {"goal": 9, "project": 8, "preference": 6, "problem": 7}.get(mem_type, 5)

    def _tags(self, content: str, mem_type: str) -> list[str]:
        words = content.lower().split()
        stopwords = {"a", "an", "the", "to", "in", "on", "at", "for", "of", "with", "and", "or", "it", "is", "my", "i"}
        tags = [w.strip(",:.") for w in words if w not in stopwords and len(w) > 2]
        tags.append(mem_type)
        return tags[:6]

    def _clean_content(self, raw: str, msg: str, mem_type: str) -> str:
        if mem_type == "goal":
            if " to " in raw:
                parts = raw.split(" to ", 1)
                return (parts[0].strip() + ": " + parts[1].strip()).capitalize()
            return raw.capitalize()
        return raw.capitalize()
