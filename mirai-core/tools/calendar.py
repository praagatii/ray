from datetime import datetime, timedelta
from tools.registry import BaseTool, ToolResult


class CalendarTool(BaseTool):
    name = "calendar"
    description = "Manage calendar events - create, list, or check events"
    parameters = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["list", "create", "check"],
                "description": "Action to perform"
            },
            "title": {"type": "string", "description": "Event title"},
            "time": {"type": "string", "description": "Event time (ISO format)"},
            "duration": {"type": "integer", "description": "Duration in minutes"}
        },
        "required": ["action"]
    }

    def __init__(self):
        self.events = []

    def execute(self, action: str = "list", title: str = "", time: str = "", duration: int = 60, **kwargs) -> ToolResult:
        if action == "list":
            now = datetime.now()
            today_events = [e for e in self.events if e["time"].startswith(now.strftime("%Y-%m-%d"))]
            if today_events:
                lines = [f"{e['time'][:16]} - {e['title']} ({e['duration']}min)" for e in today_events]
                return ToolResult(tool_name=self.name, content="Today's events:\n" + "\n".join(lines))
            return ToolResult(tool_name=self.name, content="No events today")

        elif action == "create":
            event = {
                "title": title or "Untitled",
                "time": time or datetime.now().isoformat(),
                "duration": duration
            }
            self.events.append(event)
            return ToolResult(tool_name=self.name, content=f"Created event: {title} at {time[:16]}")

        elif action == "check":
            now = datetime.now()
            upcoming = [e for e in self.events if e["time"] > now.isoformat()]
            upcoming.sort(key=lambda x: x["time"])
            if upcoming:
                next_e = upcoming[0]
                return ToolResult(tool_name=self.name, content=f"Next event: {next_e['title']} at {next_e['time'][:16]}")
            return ToolResult(tool_name=self.name, content="No upcoming events")

        return ToolResult(tool_name=self.name, content=f"Unknown action: {action}", success=False)
