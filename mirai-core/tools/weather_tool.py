import httpx
from tools.registry import BaseTool, ToolResult


class WeatherTool(BaseTool):
    name = "weather"
    description = "Get current weather for a location"
    parameters = {
        "type": "object",
        "properties": {
            "location": {"type": "string", "description": "City name or location"}
        },
        "required": ["location"]
    }

    def execute(self, location: str = "", **kwargs) -> ToolResult:
        try:
            url = f"https://wttr.in/{httpx.utils.quote(location)}?format=%C+%t+%h+%w"
            resp = httpx.get(url, timeout=10)
            return ToolResult(tool_name=self.name, content=f"Weather in {location}: {resp.text}")
        except Exception as e:
            return ToolResult(tool_name=self.name, content=f"Weather error: {e}", success=False, error=str(e))
