from tools.registry import BaseTool, ToolResult


class ContactLookupTool(BaseTool):
    name = "contact_lookup"
    description = "Look up a contact by name or list all contacts"
    parameters = {
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "Contact name to search for"}
        }
    }

    def __init__(self):
        self.contacts = [
            {"name": "Mom", "phone": "Mom's phone", "email": "mom@email.com"},
            {"name": "Dad", "phone": "Dad's phone", "email": "dad@email.com"},
            {"name": "John", "phone": "555-0100", "email": "john@email.com"},
        ]

    def execute(self, name: str = "", **kwargs) -> ToolResult:
        if not name:
            lines = [f"{c['name']}: {c.get('phone', '')}" for c in self.contacts]
            return ToolResult(tool_name=self.name, content="Contacts:\n" + "\n".join(lines))

        results = [c for c in self.contacts if name.lower() in c["name"].lower()]
        if results:
            c = results[0]
            return ToolResult(tool_name=self.name, content=f"{c['name']}: {c.get('phone', 'N/A')} | {c.get('email', 'N/A')}")
        return ToolResult(tool_name=self.name, content=f"No contact found: {name}", success=False)
