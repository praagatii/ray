import subprocess
import platform
import os
import time
from datetime import datetime
from .tool_registry import BaseRuntimeTool, ToolResult

DESTRUCTIVE_COMMANDS = {
    "rm", "del", "rd", "rmdir", "format", "diskpart", "dd",
    "shutdown", "reboot", "halt", "poweroff",
    "chmod", "chown", "kill", "pkill", "taskkill",
    "reg delete", "regedit", "sc delete",
    ">", ">>", "|", "format", "fdisk", "mkfs",
    "mount", "umount", "init",
}


def _is_destructive(command: str) -> bool:
    lower = command.strip().lower()
    for kw in DESTRUCTIVE_COMMANDS:
        if lower.startswith(kw) and (len(lower) == len(kw) or lower[len(kw)] in " /-"):
            return True
    return False


class ShellTool(BaseRuntimeTool):
    name = "shell"
    description = "Execute a shell command on the host system. Destructive commands require explicit confirmation."
    category = "system"
    parameters = {
        "type": "object",
        "properties": {
            "command": {"type": "string", "description": "Shell command to execute"},
            "workdir": {"type": "string", "description": "Working directory (default: project root)"},
            "timeout": {"type": "integer", "description": "Timeout in seconds", "default": 30},
            "confirmed": {"type": "boolean", "description": "Set to true to confirm destructive commands", "default": False},
        },
        "required": ["command"],
    }

    def __init__(self):
        self.executed_commands: list[dict] = []

    def execute(self, command: str = "", workdir: str = "", timeout: int = 30, confirmed: bool = False, **kwargs) -> ToolResult:
        try:
            if _is_destructive(command):
                if not confirmed:
                    return ToolResult(
                        tool_name=self.name,
                        content=f"Destructive command blocked: `{command}`\nSet confirmed=true to allow.",
                        success=False,
                        error="Destructive command requires confirmation",
                    )

            cwd = workdir or os.getcwd()
            shell_flag = True if platform.system() == "Windows" else False
            start = time.time()
            result = subprocess.run(
                command,
                shell=shell_flag,
                capture_output=True,
                text=True,
                cwd=cwd,
                timeout=timeout,
            )
            elapsed = time.time() - start
            output = result.stdout or ""
            if result.stderr:
                output += "\nSTDERR:\n" + result.stderr
            output = output[:5000]

            self.executed_commands.append({
                "command": command,
                "cwd": cwd,
                "timestamp": datetime.now().isoformat(),
                "duration_s": round(elapsed, 2),
                "exit_code": result.returncode,
            })

            return ToolResult(
                tool_name=self.name,
                content=output or f"Exit code: {result.returncode}",
                success=result.returncode == 0,
            )
        except subprocess.TimeoutExpired:
            return ToolResult(tool_name=self.name, content="Command timed out", success=False, error="Timeout")
        except Exception as e:
            return ToolResult(tool_name=self.name, content=str(e), success=False, error=str(e))

    def get_history(self) -> list[dict]:
        return self.executed_commands[-20:]


class PythonEvalTool(BaseRuntimeTool):
    name = "python_eval"
    description = "Execute Python code and return the result. Only safe builtins are available."
    category = "system"
    parameters = {
        "type": "object",
        "properties": {
            "code": {"type": "string", "description": "Python code to execute"},
            "timeout": {"type": "integer", "description": "Timeout in seconds", "default": 15},
        },
        "required": ["code"],
    }

    def execute(self, code: str = "", timeout: int = 15, **kwargs) -> ToolResult:
        import io
        import sys
        import traceback
        import builtins
        try:
            safe_builtins = {}
            for name in ["print", "len", "str", "int", "float", "list", "dict", "tuple", "set",
                          "range", "enumerate", "zip", "map", "filter", "sorted", "reversed",
                          "min", "max", "sum", "abs", "round", "bool", "type", "True", "False",
                          "None", "Exception", "ValueError", "TypeError", "KeyError", "IndexError",
                          "isinstance", "hasattr", "getattr", "setattr", "dir", "locals", "globals"]:
                if hasattr(builtins, name):
                    safe_builtins[name] = getattr(builtins, name)

            old_stdout = sys.stdout
            sys.stdout = buffer = io.StringIO()
            exec_globals = {"__builtins__": safe_builtins}
            exec(code, exec_globals)
            sys.stdout = old_stdout
            output = buffer.getvalue()
            return ToolResult(tool_name=self.name, content=output or "Code executed (no output)")
        except Exception as e:
            return ToolResult(
                tool_name=self.name,
                content=traceback.format_exc()[-2000:],
                success=False,
                error=str(e),
            )
        finally:
            sys.stdout = old_stdout
