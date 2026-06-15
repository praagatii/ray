import os
from pathlib import Path
from tools.registry import BaseTool, ToolResult


class FileSearchTool(BaseTool):
    name = "file_search"
    description = "Search for files on the device by name or pattern"
    parameters = {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Filename or pattern to search for"},
            "directory": {"type": "string", "description": "Directory to search in (default: home)"}
        },
        "required": ["query"]
    }

    def execute(self, query: str = "", directory: str = "", **kwargs) -> ToolResult:
        search_dir = directory or str(Path.home())
        results = []
        try:
            for root, dirs, files in os.walk(search_dir):
                try:
                    for f in files:
                        if query.lower() in f.lower():
                            results.append(os.path.join(root, f))
                except PermissionError:
                    continue
                if len(results) >= 20:
                    break
        except Exception as e:
            return ToolResult(tool_name=self.name, content=str(e), success=False, error=str(e))

        if results:
            content = "\n".join(results[:20])
            return ToolResult(tool_name=self.name, content=f"Found {len(results)} files:\n{content}")
        return ToolResult(tool_name=self.name, content=f"No files found matching '{query}'")


class FileReadTool(BaseTool):
    name = "file_read"
    description = "Read the contents of a file"
    parameters = {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Full path to the file"}
        },
        "required": ["path"]
    }

    def execute(self, path: str = "", **kwargs) -> ToolResult:
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            return ToolResult(tool_name=self.name, content=content[:5000])
        except Exception as e:
            return ToolResult(tool_name=self.name, content=str(e), success=False, error=str(e))
