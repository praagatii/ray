import subprocess
import os
from pathlib import Path
from .tool_registry import BaseRuntimeTool, ToolResult


class AndroidBuildTool(BaseRuntimeTool):
    name = "android_build"
    description = "Build an Android project using Gradle"
    category = "android"
    parameters = {
        "type": "object",
        "properties": {
            "project_dir": {"type": "string", "description": "Android project directory"},
            "task": {"type": "string", "description": "Gradle task (default: assembleDebug)", "default": "assembleDebug"},
            "args": {"type": "string", "description": "Additional Gradle arguments"},
        },
        "required": ["project_dir"],
    }

    def execute(self, project_dir: str = "", task: str = "assembleDebug", args: str = "", **kwargs) -> ToolResult:
        try:
            gradlew = Path(project_dir) / "gradlew.bat"
            if not gradlew.exists():
                gradlew = Path(project_dir) / "gradlew"
            if not gradlew.exists():
                return ToolResult(
                    tool_name=self.name,
                    content=f"gradlew not found in {project_dir}",
                    success=False,
                )
            full_args = f'"{gradlew}" {task} {args} --no-daemon'
            result = subprocess.run(
                full_args,
                shell=True,
                capture_output=True,
                text=True,
                cwd=project_dir,
                timeout=300,
            )
            output = (result.stdout or "")[-4000:]
            if result.stderr:
                output += "\nSTDERR:\n" + result.stderr[-1000:]
            return ToolResult(
                tool_name=self.name,
                content=output or f"Exit code: {result.returncode}",
                success=result.returncode == 0,
            )
        except subprocess.TimeoutExpired:
            return ToolResult(tool_name=self.name, content="Build timed out (5 min limit)", success=False)
        except Exception as e:
            return ToolResult(tool_name=self.name, content=str(e), success=False, error=str(e))


class AndroidAdbTool(BaseRuntimeTool):
    name = "android_adb"
    description = "Run an ADB command on a connected device or emulator"
    category = "android"
    parameters = {
        "type": "object",
        "properties": {
            "args": {"type": "string", "description": "ADB arguments (e.g. 'shell ls /sdcard')"},
        },
        "required": ["args"],
    }

    def execute(self, args: str = "", **kwargs) -> ToolResult:
        try:
            result = subprocess.run(
                f"adb {args}",
                shell=True, capture_output=True, text=True, timeout=15,
            )
            output = result.stdout or ""
            if result.stderr:
                output += "\n" + result.stderr
            return ToolResult(
                tool_name=self.name,
                content=output[:3000] or f"Exit code: {result.returncode}",
                success=result.returncode == 0,
            )
        except FileNotFoundError:
            return ToolResult(tool_name=self.name, content="ADB not found on PATH", success=False)
        except Exception as e:
            return ToolResult(tool_name=self.name, content=str(e), success=False, error=str(e))


# --- Future Android Bridge Stubs ---

class AndroidNotificationTool(BaseRuntimeTool):
    name = "android_notification"
    description = "[BRIDGE] Send a notification to the Android device"
    category = "android_bridge"
    parameters = {
        "type": "object",
        "properties": {
            "title": {"type": "string", "description": "Notification title"},
            "text": {"type": "string", "description": "Notification body text"},
            "priority": {"type": "string", "description": "Priority: low, normal, high", "default": "normal"},
        },
        "required": ["title", "text"],
    }

    def execute(self, title: str = "", text: str = "", priority: str = "normal", **kwargs) -> ToolResult:
        return ToolResult(
            tool_name=self.name,
            content=f"[BRIDGE NOT IMPLEMENTED] Would send notification: {title} - {text}",
            success=False,
            error="Android bridge not yet connected",
        )


class AndroidIntentTool(BaseRuntimeTool):
    name = "android_intent"
    description = "[BRIDGE] Launch an Android intent (open app, URL, share, etc.)"
    category = "android_bridge"
    parameters = {
        "type": "object",
        "properties": {
            "action": {"type": "string", "description": "Intent action (ACTION_VIEW, ACTION_SEND, etc.)"},
            "data": {"type": "string", "description": "Intent data URI"},
            "package": {"type": "string", "description": "Target package name"},
        },
        "required": ["action"],
    }

    def execute(self, action: str = "", data: str = "", package: str = "", **kwargs) -> ToolResult:
        return ToolResult(
            tool_name=self.name,
            content=f"[BRIDGE NOT IMPLEMENTED] Would fire intent: {action} {data or ''} {package or ''}",
            success=False,
            error="Android bridge not yet connected",
        )


class AndroidAppsTool(BaseRuntimeTool):
    name = "android_apps"
    description = "[BRIDGE] List or launch apps on the Android device"
    category = "android_bridge"
    parameters = {
        "type": "object",
        "properties": {
            "action": {"type": "string", "description": "list or launch", "default": "list"},
            "package_name": {"type": "string", "description": "Package name to launch (required for action=launch)"},
        },
    }

    def execute(self, action: str = "list", package_name: str = "", **kwargs) -> ToolResult:
        if action == "list":
            return ToolResult(
                tool_name=self.name,
                content="[BRIDGE NOT IMPLEMENTED] Would list installed apps",
                success=False,
                error="Android bridge not yet connected",
            )
        if action == "launch" and package_name:
            return ToolResult(
                tool_name=self.name,
                content=f"[BRIDGE NOT IMPLEMENTED] Would launch {package_name}",
                success=False,
                error="Android bridge not yet connected",
            )
        return ToolResult(tool_name=self.name, content="Invalid usage", success=False)


class AndroidContactsTool(BaseRuntimeTool):
    name = "android_contacts"
    description = "[BRIDGE] Search or manage contacts on the Android device"
    category = "android_bridge"
    parameters = {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search term for contact name or number"},
            "action": {"type": "string", "description": "search, list (default: search)"},
        },
    }

    def execute(self, query: str = "", action: str = "search", **kwargs) -> ToolResult:
        return ToolResult(
            tool_name=self.name,
            content=f"[BRIDGE NOT IMPLEMENTED] Would {action} contacts matching '{query or '(all)'}'",
            success=False,
            error="Android bridge not yet connected",
        )


class AndroidCalendarTool(BaseRuntimeTool):
    name = "android_calendar"
    description = "[BRIDGE] Read or create calendar events on the Android device"
    category = "android_bridge"
    parameters = {
        "type": "object",
        "properties": {
            "action": {"type": "string", "description": "list, create (default: list)"},
            "title": {"type": "string", "description": "Event title (required for action=create)"},
            "when": {"type": "string", "description": "Event date/time in ISO format"},
        },
    }

    def execute(self, action: str = "list", title: str = "", when: str = "", **kwargs) -> ToolResult:
        return ToolResult(
            tool_name=self.name,
            content=f"[BRIDGE NOT IMPLEMENTED] Would {action} calendar event '{title or '(all)'}'",
            success=False,
            error="Android bridge not yet connected",
        )
