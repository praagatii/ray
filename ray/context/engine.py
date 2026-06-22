import time
from ray.memory.long_term import LongTermMemory
from ray.memory.identity import IdentityMemory

STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "i", "you", "he", "she",
    "it", "we", "they", "my", "your", "his", "her", "its", "our", "their",
    "me", "him", "us", "them", "in", "on", "at", "to", "for", "of", "with",
    "by", "from", "as", "about", "into", "through", "during", "and", "but",
    "or", "nor", "not", "so", "yet", "if", "because", "while", "do", "does",
    "did", "have", "has", "had", "this", "that", "these", "those", "am", "be",
    "been", "being", "very", "just", "really", "like", "some", "can", "will",
    "don't", "isn't", "aren't", "wasn't", "weren't", "it's", "that's",
    "doesn't", "didn't", "feeling", "feel", "feels", "felt"
}


class ContextEngine:
    def __init__(self):
        self.ltm = LongTermMemory()
        self.idm = IdentityMemory()

    def build_context(self, input_data: dict) -> dict:
        text = input_data.get("text", "")

        keywords = self._extract_keywords(text)
        t0 = time.time()
        memories = self._search_memories(keywords)
        search_time = time.time() - t0
        identity = self.idm.get_identity()

        if not memories:
            t0 = time.time()
            memories = self._identity_fallback(identity)
            search_time += time.time() - t0

        summary = self._generate_summary(text, memories, identity)

        return {
            "current_input": input_data,
            "relevant_memories": memories,
            "user_identity": identity,
            "context_summary": summary,
            "_search_time": search_time
        }

    def _extract_keywords(self, text: str) -> list[str]:
        words = text.lower().split()
        return [w for w in words if w not in STOPWORDS and len(w) > 2]

    def _search_memories(self, keywords: list[str]) -> list[dict]:
        seen_ids = set()
        results = []
        for kw in keywords:
            for scored in self.ltm.search(kw):
                mem_id = scored["memory"]["id"]
                if mem_id not in seen_ids:
                    seen_ids.add(mem_id)
                    mem = dict(scored["memory"])
                    mem["_score"] = scored["score"]
                    mem["_reason"] = scored["reason"]
                    results.append(mem)
        results.sort(key=lambda m: m.get("_score", 0), reverse=True)
        return results

    def _identity_fallback(self, identity: dict) -> list[dict]:
        fallbacks = []
        seen = set()
        project_names = identity.get("projects", [])

        for project in project_names:
            entry = {
                "id": f"idp_{project[:20]}",
                "type": "project",
                "content": project,
                "importance": 5
            }
            seen.add(project)
            fallbacks.append(entry)

        for project in project_names:
            name = project.split(":")[0].split(" ")[0].strip().lower()
            if len(name) > 2:
                for scored in self.ltm.search(name):
                    mem = scored["memory"]
                    if mem["content"] not in seen:
                        seen.add(mem["content"])
                        mem_copy = dict(mem)
                        mem_copy["importance"] = mem.get("importance", 1) + 2
                        fallbacks.append(mem_copy)

        fallbacks.sort(key=lambda m: m["importance"], reverse=True)
        return fallbacks

    def _generate_summary(self, text: str, memories: list[dict], identity: dict) -> str:
        if not memories:
            name = identity.get("name", "User")
            return f"No direct keyword match. {name}'s active projects may be relevant context."

        top = memories[0]
        return (
            f"User may be referring to related context. "
            f"Top memory: [{top['type']}] {top['content']}. "
            f"Matched {len(memories)} relevant memory/memories."
        )
