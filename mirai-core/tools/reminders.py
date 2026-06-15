from datetime import datetime
from tools.registry import BaseTool, ToolResult


class ReminderTool(BaseTool):
    name = "reminder"
    description = "Create, list, or check reminders"
    parameters = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["create", "list", "check"],
                "description": "Action to perform"
            },
            "title": {"type": "string", "description": "Reminder text"},
            "time": {"type": "string", "description": "When to remind (ISO format or relative like 'in 30 minutes')"}
        },
        "required": ["action"]
    }

    def __init__(self):
        self.reminders = []

    def execute(self, action: str = "list", title: str = "", time: str = "", **kwargs) -> ToolResult:
        if action == "create":
            reminder = {
                "title": title,
                "time": time or datetime.now().isoformat(),
                "created_at": datetime.now().isoformat()
            }
            self.reminders.append(reminder)
            return ToolResult(tool_name=self.name, content=f"Reminder set: {title}")

        elif action == "list":
            if not self.reminders:
                return ToolResult(tool_name=self.name, content="No reminders")
            lines = [f"{r['time'][:16]} - {r['title']}" for r in self.reminders]
            return ToolResult(tool_name=self.name, content="Reminders:\n" + "\n".join(lines))

        elif action == "check":
            now = datetime.now()
            due = [r for r in self.reminders if r["time"] <= now.isoformat()]
            if due:
                lines = [f"REMINDER: {r['title']}" for r in due]
                return ToolResult(tool_name=self.name, content="\n".join(lines))
            return ToolResult(tool_name=self.name, content="No due reminders")

        return ToolResult(tool_name=self.name, content=f"Unknown action: {action}", success=False)
