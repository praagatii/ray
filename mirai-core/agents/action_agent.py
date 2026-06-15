from models.engine import LLMEngine
from typing import Optional
from tools.registry import ToolRegistry


class ActionAgent:
    def __init__(self, engine: LLMEngine, tool_registry: ToolRegistry):
        self.engine = engine
        self.tools = tool_registry

    def execute_intent(self, intent: str, params: dict = None) -> str:
        tool_name = self._select_tool(intent)
        if tool_name and self.tools.has(tool_name):
            result = self.tools.execute(tool_name, **(params or {}))
            return result.content
        return f"No tool available for intent: {intent}"

    def _select_tool(self, intent: str) -> Optional[str]:
        intent_lower = intent.lower()
        tool_map = {
            "open_app": "open_app",
            "calendar": "calendar",
            "reminder": "reminder",
            "file": "file_search",
            "contact": "contact_lookup",
            "notification": "notification",
            "search": "web_search",
            "calculate": "calculator",
            "weather": "weather",
        }
        for keyword, tool in tool_map.items():
            if keyword in intent_lower:
                return tool
        return None

    def plan(self, goal: str) -> list[str]:
        prompt = f"Break down this goal into a step-by-step plan:\n{goal}\n\nReturn as a numbered list."
        messages = [
            {"role": "system", "content": "You are a planning agent. Break goals into actionable steps."},
            {"role": "user", "content": prompt}
        ]
        response = self.engine.generate(messages)
        steps = [s.strip() for s in response.split("\n") if s.strip() and s[0].isdigit()]
        return steps if steps else [response]
