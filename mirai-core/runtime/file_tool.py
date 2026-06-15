import os
from pathlib import Path
from .tool_registry import BaseRuntimeTool, ToolResult

ALLOWED_WORKSPACES = []


def set_allowed_workspaces(paths: list[str]):
    global ALLOWED_WORKSPACES
    resolved = []
    for p in paths:
        rp = Path(p).resolve()
        if rp.exists():
            resolved.append(str(rp))
    ALLOWED_WORKSPACES = resolved


def _check_path(path: str, write: bool = False) -> tuple[Path, str]:
    p = Path(path).resolve()
    if not ALLOWED_WORKSPACES:
        return p, ""
    allowed = False
    for ws in ALLOWED_WORKSPACES:
        try:
            p.relative_to(ws)
            allowed = True
            break
        except ValueError:
            continue
    if not allowed:
        return p, f"Access denied: {p} is outside allowed workspaces: {', '.join(ALLOWED_WORKSPACES)}"
    return p, ""


class FileReadTool(BaseRuntimeTool):
    name = "file_read"
    description = "Read the contents of a file"
    category = "filesystem"
    parameters = {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Absolute or relative path to the file"},
        },
        "required": ["path"],
    }

    def execute(self, path: str = "", **kwargs) -> ToolResult:
        try:
            p, err = _check_path(path)
            if err:
                return ToolResult(tool_name=self.name, content=err, success=False)
            if not p.exists():
                return ToolResult(tool_name=self.name, content=f"File not found: {p}", success=False)
            content = p.read_text(encoding="utf-8")
            return ToolResult(tool_name=self.name, content=content)
        except Exception as e:
            return ToolResult(tool_name=self.name, content=str(e), success=False, error=str(e))


class FileWriteTool(BaseRuntimeTool):
    name = "file_write"
    description = "Write content to a file (creates directories if needed)"
    category = "filesystem"
    parameters = {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "File path to write to"},
            "content": {"type": "string", "description": "Content to write"},
        },
        "required": ["path", "content"],
    }

    def execute(self, path: str = "", content: str = "", **kwargs) -> ToolResult:
        try:
            p, err = _check_path(path, write=True)
            if err:
                return ToolResult(tool_name=self.name, content=err, success=False)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")
            size = p.stat().st_size
            return ToolResult(tool_name=self.name, content=f"Wrote {size} bytes to {p}")
        except Exception as e:
            return ToolResult(tool_name=self.name, content=str(e), success=False, error=str(e))


class FileEditTool(BaseRuntimeTool):
    name = "file_edit"
    description = "Edit a file by replacing text (search and replace)"
    category = "filesystem"
    parameters = {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "File path to edit"},
            "old_string": {"type": "string", "description": "Text to find (must be unique)"},
            "new_string": {"type": "string", "description": "Replacement text"},
        },
        "required": ["path", "old_string", "new_string"],
    }

    def execute(self, path: str = "", old_string: str = "", new_string: str = "", **kwargs) -> ToolResult:
        try:
            p, err = _check_path(path, write=True)
            if err:
                return ToolResult(tool_name=self.name, content=err, success=False)
            if not p.exists():
                return ToolResult(tool_name=self.name, content=f"File not found: {p}", success=False)
            text = p.read_text(encoding="utf-8")
            count = text.count(old_string)
            if count == 0:
                return ToolResult(tool_name=self.name, content=f"String not found in {p}", success=False)
            text = text.replace(old_string, new_string, 1)
            p.write_text(text, encoding="utf-8")
            return ToolResult(tool_name=self.name, content=f"Replaced 1 occurrence in {p}")
        except Exception as e:
            return ToolResult(tool_name=self.name, content=str(e), success=False, error=str(e))


class FileListTool(BaseRuntimeTool):
    name = "file_list"
    description = "List files and directories in a path"
    category = "filesystem"
    parameters = {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Directory path (default: current)"},
            "pattern": {"type": "string", "description": "Optional glob pattern to filter"},
        },
    }

    def execute(self, path: str = "", pattern: str = "", **kwargs) -> ToolResult:
        try:
            p, err = _check_path(path or ".")
            if err:
                return ToolResult(tool_name=self.name, content=err, success=False)
            if not p.is_dir():
                return ToolResult(tool_name=self.name, content=f"Not a directory: {p}", success=False)
            items = list(p.iterdir())
            lines = []
            for item in sorted(items):
                suffix = "/" if item.is_dir() else ""
                lines.append(f"{item.name}{suffix}")
            return ToolResult(tool_name=self.name, content="\n".join(lines) or "(empty)")
        except Exception as e:
            return ToolResult(tool_name=self.name, content=str(e), success=False, error=str(e))
