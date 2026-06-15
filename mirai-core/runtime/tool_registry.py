from typing import Optional
from pydantic import BaseModel


class ToolSpec(BaseModel):
    name: str
    description: str
    parameters: dict = {}
    category: str = "general"


class ToolResult(BaseModel):
    tool_name: str
    content: str
    success: bool = True
    error: Optional[str] = None


class BaseRuntimeTool:
    name: str = ""
    description: str = ""
    parameters: dict = {}
    category: str = "general"

    @property
    def spec(self) -> ToolSpec:
        return ToolSpec(
            name=self.name,
            description=self.description,
            parameters=self.parameters,
            category=self.category,
        )

    def execute(self, **kwargs) -> ToolResult:
        raise NotImplementedError


class RuntimeToolRegistry:
    def __init__(self):
        self._tools: dict[str, BaseRuntimeTool] = {}

    def register(self, tool: BaseRuntimeTool):
        self._tools[tool.name] = tool

    def get(self, name: str) -> Optional[BaseRuntimeTool]:
        return self._tools.get(name)

    def has(self, name: str) -> bool:
        return name in self._tools

    def execute(self, name: str, **kwargs) -> ToolResult:
        tool = self.get(name)
        if not tool:
            return ToolResult(tool_name=name, content=f"Tool '{name}' not found", success=False, error="Not found")
        try:
            return tool.execute(**kwargs)
        except Exception as e:
            return ToolResult(tool_name=name, content=str(e), success=False, error=str(e))

    def list_tools(self, category: str = "") -> list[ToolSpec]:
        if category:
            return [t.spec for t in self._tools.values() if t.category == category]
        return [t.spec for t in self._tools.values()]

    def get_openai_tools(self) -> list[dict]:
        return [{
            "type": "function",
            "function": {
                "name": t.name,
                "description": t.description,
                "parameters": t.parameters or {"type": "object", "properties": {}},
            }
        } for t in self._tools.values()]
