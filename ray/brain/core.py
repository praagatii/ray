import time
from datetime import datetime, timezone

from ray.input.processor import InputProcessor
from ray.context.engine import ContextEngine
from ray.memory.short_term import ShortTermMemory
from ray.reasoning.model_provider import get_provider
from ray.reflection.reflector import ReflectionEngine
from ray import config


class RayCore:
    def __init__(self):
        self.input_processor = InputProcessor()
        self.context_engine = ContextEngine()
        self.short_term = ShortTermMemory()
        self.reflection = ReflectionEngine()

    def startup(self):
        print("Ray starting...")
        print(f"  Config: {config.MODEL_PROVIDER} / {config.OLLAMA_MODEL}")
        print("  Memory: loaded")
        print("  Identity: loaded")
        self.model = get_provider()
        print(f"  Brain: {self.model.info()}")
        print("Ray ready.")

    def shutdown(self):
        self.short_term._write(self.short_term._read())
        print("Memory saved. Goodbye.")

    def _detect_mode(self, text: str) -> str:
        short = text.strip().lower()
        if len(short.split()) <= 4:
            return "chat"
        deep_indicators = ["remember", "what do you know", "tell me about", "who am i",
                           "what did", "recall", "history", "explain"]
        if any(ind in short for ind in deep_indicators):
            return "deep"
        return "chat"

    def process_message(self, user_text: str, _timing: bool = False) -> dict:
        timing = {}

        t0 = time.time()
        processed = self.input_processor.process(user_text)
        timing["input_process"] = time.time() - t0

        t0 = time.time()
        self.short_term.add(processed["text"])
        timing["short_term_write"] = time.time() - t0

        t0 = time.time()
        context = self.context_engine.build_context(processed)
        timing["context_build"] = time.time() - t0

        memory_time = context.get("_search_time", 0)
        if memory_time:
            timing["memory_retrieval"] = memory_time

        mode = self._detect_mode(user_text)
        context["mode"] = mode
        timing["mode"] = mode

        t0 = time.time()
        reasoning_result = self.model.think(context)
        timing["ollama_generation"] = time.time() - t0

        context_used = [
            m["content"] for m in context.get("relevant_memories", [])
        ]

        interaction = {
            "user_message": user_text,
            "ray_response": reasoning_result["response"],
            "context_used": context_used
        }
        t0 = time.time()
        reflection_result = self.reflection.reflect(interaction)
        self.reflection.store(reflection_result)
        timing["reflection"] = time.time() - t0

        result = {
            "user_message": user_text,
            "ray_response": reasoning_result["response"],
            "context_used": context_used,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        if _timing:
            result["_timing"] = timing

        return result
