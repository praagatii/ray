import json
from datetime import datetime
from models.engine import LLMEngine
from memory.short_term import ShortTermMemory
from memory.long_term import LongTermMemory


class MemoryAgent:
    def __init__(self, engine: LLMEngine, stm: ShortTermMemory, ltm: LongTermMemory):
        self.engine = engine
        self.stm = stm
        self.ltm = ltm

    def store_conversation(self, user_input: str, response: str, metadata: dict = None):
        entry = {
            "input": user_input,
            "response": response,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        self.stm.add(entry)
        self.ltm.store(
            content=f"User: {user_input}\nAssistant: {response}",
            source="conversation",
            metadata=metadata or {}
        )

    def recall(self, query: str, top_k: int = 5) -> list[dict]:
        stm_results = self.stm.search(query, top_k)
        ltm_results = self.ltm.search(query, top_k)
        combined = stm_results + ltm_results
        combined.sort(key=lambda x: x.get("score", 0) if isinstance(x, dict) else x.get("score", 0), reverse=True)
        return combined[:top_k]

    def summarize_memory(self) -> str:
        recent = self.stm.get_recent(10)
        if not recent:
            return "No recent conversations."
        prompt = f"Summarize the key information from these recent interactions:\n{json.dumps(recent, indent=2)}"
        messages = [
            {"role": "system", "content": "Extract key facts, preferences, and context from these interactions."},
            {"role": "user", "content": prompt}
        ]
        return self.engine.generate(messages)

    def get_user_preferences(self) -> dict:
        memories = self.ltm.search("user preferences likes dislikes habits", top_k=20)
        prefs = {}
        for m in memories:
            content = m.get("content", "")
            if "preference" in content.lower() or "like" in content.lower() or "habit" in content.lower():
                prefs[m.get("id", "")] = content
        return prefs
