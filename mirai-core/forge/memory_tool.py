import json
from datetime import datetime
from forge.tool_registry import BaseRuntimeTool, ToolResult


class MemoryStoreTool(BaseRuntimeTool):
    name = "memory_store"
    description = "Store information in Mirai's long-term memory for future recall"
    category = "memory"
    parameters = {
        "type": "object",
        "properties": {
            "content": {"type": "string", "description": "Information to remember"},
            "tags": {"type": "string", "description": "Comma-separated tags for retrieval"},
            "source": {"type": "string", "description": "Source label (default: agent)"},
        },
        "required": ["content"],
    }

    def __init__(self, memory_backend=None):
        self.memory = memory_backend

    def execute(self, content: str = "", tags: str = "", source: str = "agent", **kwargs) -> ToolResult:
        if not content:
            return ToolResult(tool_name=self.name, content="Nothing to store", success=False)
        if self.memory:
            self.memory.store(
                content=content,
                source=source,
                metadata={"tags": tags, "stored_at": datetime.now().isoformat()}
            )
            return ToolResult(tool_name=self.name, content=f"Stored in memory: {content[:100]}")
        return ToolResult(tool_name=self.name, content="Memory backend not available", success=False)


class MemoryRecallTool(BaseRuntimeTool):
    name = "memory_recall"
    description = "Recall information from long-term memory by searching"
    category = "memory"
    parameters = {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "What to search for in memory"},
            "limit": {"type": "integer", "description": "Max results", "default": 5},
        },
        "required": ["query"],
    }

    def __init__(self, memory_backend=None):
        self.memory = memory_backend

    def execute(self, query: str = "", limit: int = 5, **kwargs) -> ToolResult:
        if not query:
            return ToolResult(tool_name=self.name, content="No query provided", success=False)
        if self.memory:
            results = self.memory.search(query, top_k=limit)
            if results:
                lines = [f"[{r.get('timestamp', '')[:19]}] {r.get('content', '')[:200]}" for r in results]
                return ToolResult(
                    tool_name=self.name,
                    content=f"Found {len(results)} memory result(s):\n" + "\n".join(lines)
                )
            return ToolResult(tool_name=self.name, content="No relevant memories found")
        return ToolResult(tool_name=self.name, content="Memory backend not available", success=False)


class MemoryRecentTool(BaseRuntimeTool):
    name = "memory_recent"
    description = "Get the most recent entries from long-term memory"
    category = "memory"
    parameters = {
        "type": "object",
        "properties": {
            "limit": {"type": "integer", "description": "Number of recent entries", "default": 10},
        },
    }

    def __init__(self, memory_backend=None):
        self.memory = memory_backend

    def execute(self, limit: int = 10, **kwargs) -> ToolResult:
        if self.memory:
            results = self.memory.get_recent(limit=limit)
            if results:
                lines = [f"[{r.get('timestamp', '')[:19]}] {r.get('content', '')[:200]}" for r in results]
                return ToolResult(
                    tool_name=self.name,
                    content=f"Recent {len(results)} memories:\n" + "\n".join(lines)
                )
            return ToolResult(tool_name=self.name, content="No memories yet")
            return ToolResult(tool_name=self.name, content="Memory backend not available", success=False)
