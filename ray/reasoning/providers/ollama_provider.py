import urllib.request
import json as json_lib

from ray.reasoning.providers.base import BaseProvider
from ray.reasoning.prompts import build_prompt
from ray import config


MODE_CONFIG = {
    "chat": {
        "num_predict": 200,
        "temperature": 0.6,
    },
    "deep": {
        "num_predict": 800,
        "temperature": 0.7,
    }
}


class OllamaProvider(BaseProvider):
    def __init__(self):
        self.model = config.OLLAMA_MODEL
        self.endpoint = f"{config.OLLAMA_HOST}/api/generate"
        self.timeout = 120
        self._health_check()

    def _health_check(self):
        url = f"{config.OLLAMA_HOST}/api/tags"
        try:
            urllib.request.urlopen(url, timeout=5)
        except Exception as e:
            raise ConnectionError(f"Ollama not reachable at {config.OLLAMA_HOST}: {e}")

    def info(self) -> str:
        return f"Ollama {self.model} connected"

    def think(self, context: dict) -> dict:
        prompt = build_prompt(context)
        mode = context.get("mode", "chat")
        response = self._call_ollama(prompt, mode)
        return {
            "response": response,
            "reasoning_summary": f"ollama/{mode}",
            "model_used": f"ollama/{self.model}"
        }

    def _call_ollama(self, prompt: str, mode: str = "chat") -> str:
        opts = MODE_CONFIG.get(mode, MODE_CONFIG["chat"])

        payload = json_lib.dumps({
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": opts["num_predict"],
                "temperature": opts["temperature"],
                "stop": ["\n\n---", "\n---"]
            }
        }).encode()

        req = urllib.request.Request(
            self.endpoint,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            result = json_lib.loads(resp.read().decode())
            return result.get("response", "").strip()
