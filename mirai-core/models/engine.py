import os
from abc import ABC, abstractmethod
from typing import Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class LLMEngine(ABC):
    @abstractmethod
    def generate(self, messages: list[dict], model: Optional[str] = None, **kwargs) -> str:
        pass

    @abstractmethod
    def name(self) -> str:
        pass


class OpenRouterEngine(LLMEngine):
    def __init__(self, api_key: Optional[str] = None):
        self._api_key = api_key or os.getenv("OPENROUTER_API_KEY", "")
        self._model = os.getenv("OPENROUTER_MODEL", "deepseek/deepseek-chat")
        self._name = "openrouter"

    def name(self) -> str:
        return self._name

    def generate(self, messages: list[dict], model: Optional[str] = None, **kwargs) -> str:
        import httpx
        model_name = model or self._model
        url = "https://openrouter.ai/api/v1/chat/completions"
        body = {
            "model": model_name,
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 2048),
        }
        if kwargs.get("response_format"):
            body["response_format"] = kwargs["response_format"]

        resp = httpx.post(
            url,
            json=body,
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:8765",
                "X-Title": "Mirai",
            },
            timeout=120
        )
        data = resp.json()
        try:
            return data["choices"][0]["message"]["content"] or ""
        except (KeyError, IndexError):
            return f"OpenRouter error: {data.get('error', {}).get('message', str(data)[:200])}"


class OpenAIEngine(LLMEngine):
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        from openai import OpenAI
        self.client = OpenAI(
            api_key=api_key or os.getenv("OPENAI_API_KEY", ""),
            base_url=base_url or os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        )
        self._model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self._name = "openrouter"

    def name(self) -> str:
        return self._name

    def generate(self, messages: list[dict], model: Optional[str] = None, **kwargs) -> str:
        try:
            resp = self.client.chat.completions.create(
                model=model or self._model,
                messages=messages,
                temperature=kwargs.get("temperature", 0.7),
                max_tokens=kwargs.get("max_tokens", 2048),
                response_format=kwargs.get("response_format"),
            )
            return resp.choices[0].message.content or ""
        except Exception as e:
            return f"OpenAI-compatible API error: {str(e)[:200]}"


class GeminiEngine(LLMEngine):
    def __init__(self, api_key: Optional[str] = None):
        self._api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        self._model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
        self._name = "gemini"

    def name(self) -> str:
        return self._name

    def generate(self, messages: list[dict], model: Optional[str] = None, **kwargs) -> str:
        import httpx
        model_name = model or self._model
        system_msg = ""
        contents = []
        for msg in messages:
            if msg["role"] == "system":
                system_msg += msg["content"] + "\n"
            elif msg["role"] == "user":
                contents.append({"role": "user", "parts": [{"text": msg["content"]}]})
            elif msg["role"] == "assistant":
                contents.append({"role": "model", "parts": [{"text": msg["content"]}]})

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent"
        body = {"contents": contents}
        if system_msg.strip():
            body["systemInstruction"] = {"parts": [{"text": system_msg.strip()}]}

        resp = httpx.post(
            url,
            params={"key": self._api_key},
            json=body,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        data = resp.json()
        try:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError):
            return f"Error: {data.get('error', {}).get('message', 'Unknown error')}"


class OpenCodeEngine(LLMEngine):
    def __init__(self, server_url: str = ""):
        self._server_url = (server_url or os.getenv("OPENCODE_SERVER_URL", "http://127.0.0.1:4096")).rstrip("/")
        self._session_id: Optional[str] = None
        self._name = "opencode"

    def name(self) -> str:
        return self._name

    def _request(self, method: str, path: str, body: dict = None):
        import httpx
        url = f"{self._server_url}{path}"
        kwargs = {"timeout": 120}
        if body:
            kwargs["json"] = body
        resp = httpx.request(method, url, **kwargs)
        data = resp.json()
        if resp.status_code >= 400:
            raise RuntimeError(f"OpenCode server error: {data.get('name', resp.status_code)}")
        return data

    def _ensure_session(self):
        if self._session_id is None:
            data = self._request("POST", "/session", {})
            self._session_id = data["id"]

    def generate(self, messages: list[dict], model: Optional[str] = None, **kwargs) -> str:
        self._ensure_session()
        user_text = ""
        for m in reversed(messages):
            if m["role"] == "user":
                user_text = m["content"]
                break
        body = {"parts": [{"type": "text", "text": user_text}]}
        result = self._request("POST", f"/session/{self._session_id}/message", body)
        for part in result.get("parts", []):
            if part.get("type") == "text":
                return part["text"]
        return "No response from OpenCode"


class OllamaEngine(LLMEngine):
    def __init__(self, host: str = "http://localhost:11434"):
        self._host = os.getenv("OLLAMA_HOST", host)
        self._model = os.getenv("OLLAMA_MODEL", "qwen3.5:4b")
        self._name = "ollama"

    def name(self) -> str:
        return self._name

    def generate(self, messages: list[dict], model: Optional[str] = None, **kwargs) -> str:
        import httpx
        model_name = model or self._model
        url = f"{self._host}/api/chat"
        body = {
            "model": model_name,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": kwargs.get("temperature", 0.7),
                "num_predict": kwargs.get("max_tokens", 2048),
            }
        }
        resp = httpx.post(url, json=body, timeout=120)
        data = resp.json()
        return data.get("message", {}).get("content", "")


def get_engine(engine_type: str = "") -> LLMEngine:
    if engine_type == "openrouter":
        return OpenRouterEngine()
    if engine_type == "gemini":
        return GeminiEngine()
    if engine_type == "ollama":
        return OllamaEngine()
    if engine_type == "openai":
        return OpenAIEngine()
    if engine_type == "opencode":
        return OpenCodeEngine()

    if os.getenv("OPENCODE_SERVER_URL"):
        return OpenCodeEngine()
    if os.getenv("OPENROUTER_API_KEY"):
        return OpenRouterEngine()
    if os.getenv("GEMINI_API_KEY"):
        return GeminiEngine()
    if os.getenv("OPENAI_API_KEY"):
        return OpenAIEngine()
    return OpenRouterEngine()


def resolve_engine_info() -> dict:
    oc_url = os.getenv("OPENCODE_SERVER_URL", "")
    if oc_url:
        return {"engine": "opencode", "model": "opencode-server", "api_key_set": True, "api_key_preview": oc_url}
    key = os.getenv("OPENROUTER_API_KEY", "")
    masked = key[:8] + "..." + key[-4:] if len(key) > 12 else ""
    return {
        "engine": "openrouter",
        "model": os.getenv("OPENROUTER_MODEL", "deepseek/deepseek-chat"),
        "api_key_set": bool(key),
        "api_key_preview": masked if key else "",
    }


def has_api_key() -> bool:
    oc_url = os.getenv("OPENCODE_SERVER_URL", "")
    if oc_url:
        return True
    return bool(os.getenv("OPENROUTER_API_KEY") or os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY"))
