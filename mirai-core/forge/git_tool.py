import subprocess
import os
from pathlib import Path
from forge.tool_registry import BaseRuntimeTool, ToolResult


class GitTool(BaseRuntimeTool):
    name = "git"
    description = "Run a git command in a repository"
    category = "development"
    parameters = {
        "type": "object",
        "properties": {
            "args": {"type": "string", "description": "Git arguments (e.g. 'status', 'diff', 'log --oneline -5')"},
            "workdir": {"type": "string", "description": "Repository path (default: current)"},
        },
        "required": ["args"],
    }

    def execute(self, args: str = "", workdir: str = "", **kwargs) -> ToolResult:
        try:
            cwd = workdir or os.getcwd()
            full_cmd = f"git {args}"
            result = subprocess.run(
                full_cmd,
                shell=True,
                capture_output=True,
                text=True,
                cwd=cwd,
                timeout=30,
            )
            output = result.stdout or ""
            if result.stderr:
                output += "\n" + result.stderr
            output = output[:5000]
            return ToolResult(
                tool_name=self.name,
                content=output or f"Exit code: {result.returncode}",
                success=result.returncode == 0,
            )
        except subprocess.TimeoutExpired:
            return ToolResult(tool_name=self.name, content="Git command timed out", success=False)
        except Exception as e:
            return ToolResult(tool_name=self.name, content=str(e), success=False, error=str(e))


class GitDiffTool(BaseRuntimeTool):
    name = "git_diff"
    description = "Show uncommitted changes in the working tree"
    category = "development"
    parameters = {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Repository path (default: current)"},
            "staged": {"type": "boolean", "description": "Show staged changes only", "default": False},
        },
    }

    def execute(self, path: str = "", staged: bool = False, **kwargs) -> ToolResult:
        try:
            cwd = path or os.getcwd()
            flag = "--cached" if staged else ""
            result = subprocess.run(
                f"git diff {flag}".strip(),
                shell=True, capture_output=True, text=True, cwd=cwd, timeout=15,
            )
            content = result.stdout[:5000] or "No changes"
            return ToolResult(tool_name=self.name, content=content)
        except Exception as e:
            return ToolResult(tool_name=self.name, content=str(e), success=False, error=str(e))
