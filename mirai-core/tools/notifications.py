from tools.registry import BaseTool, ToolResult


class NotificationTool(BaseTool):
    name = "notification"
    description = "Send or list notifications"
    parameters = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["send", "list", "clear"],
                "description": "Action to perform"
            },
            "title": {"type": "string", "description": "Notification title"},
            "message": {"type": "string", "description": "Notification message"}
        },
        "required": ["action"]
    }

    def __init__(self):
        self.notifications = []

    def execute(self, action: str = "list", title: str = "", message: str = "", **kwargs) -> ToolResult:
        if action == "send":
            self.notifications.append({"title": title, "message": message})
            return ToolResult(tool_name=self.name, content=f"Notification sent: {title}")

        elif action == "list":
            if not self.notifications:
                return ToolResult(tool_name=self.name, content="No notifications")
            lines = [f"{n['title']}: {n['message']}" for n in self.notifications[-10:]]
            return ToolResult(tool_name=self.name, content="Notifications:\n" + "\n".join(lines))

        elif action == "clear":
            self.notifications.clear()
            return ToolResult(tool_name=self.name, content="Notifications cleared")

        return ToolResult(tool_name=self.name, content=f"Unknown action: {action}", success=False)
