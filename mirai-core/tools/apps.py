import subprocess
import platform
from tools.registry import BaseTool, ToolResult


class OpenAppTool(BaseTool):
    name = "open_app"
    description = "Open an application on the device"
    parameters = {
        "type": "object",
        "properties": {
            "app_name": {"type": "string", "description": "Name of the app to open"}
        },
        "required": ["app_name"]
    }

    def execute(self, app_name: str = "", **kwargs) -> ToolResult:
        system = platform.system()
        try:
            if system == "Windows":
                subprocess.Popen(["start", app_name], shell=True)
            elif system == "Darwin":
                subprocess.Popen(["open", "-a", app_name])
            elif system == "Linux":
                subprocess.Popen([app_name])
            else:
                return ToolResult(tool_name=self.name, content=f"Unsupported OS: {system}", success=False)
            return ToolResult(tool_name=self.name, content=f"Opened {app_name}")
        except Exception as e:
            return ToolResult(tool_name=self.name, content=str(e), success=False, error=str(e))


class ListAppsTool(BaseTool):
    name = "list_apps"
    description = "List installed applications"
    parameters = {
        "type": "object",
        "properties": {
            "filter": {"type": "string", "description": "Optional filter for app names"}
        }
    }

    def execute(self, filter: str = "", **kwargs) -> ToolResult:
        system = platform.system()
        try:
            if system == "Windows":
                import winreg
                apps = []
                keys = [
                    r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths",
                    r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\App Paths"
                ]
                for key_path in keys:
                    try:
                        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path)
                        i = 0
                        while True:
                            try:
                                apps.append(winreg.EnumKey(key, i))
                                i += 1
                            except WindowsError:
                                break
                    except:
                        pass
                if filter:
                    apps = [a for a in apps if filter.lower() in a.lower()]
                return ToolResult(tool_name=self.name, content="\n".join(apps[:50]) or "No apps found")
            else:
                return ToolResult(tool_name=self.name, content="App listing not supported on this OS")
        except Exception as e:
            return ToolResult(tool_name=self.name, content=str(e), success=False, error=str(e))
