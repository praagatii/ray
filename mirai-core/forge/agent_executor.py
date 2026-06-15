import json
import os
import re
import time
from enum import Enum
from typing import Optional
from datetime import datetime
from pydantic import BaseModel

from forge.tool_registry import RuntimeToolRegistry, ToolResult


class AgentMode(str, Enum):
    CHAT = "chat"
    CODER = "coder"
    ASSISTANT = "assistant"
    AUTO = "auto"


class AgentStep(BaseModel):
    thought: str = ""
    tool: Optional[str] = None
    tool_input: dict = {}
    tool_result: Optional[str] = None
    observation: str = ""
    step_number: int = 0
    duration_ms: int = 0


class AgentRunResult(BaseModel):
    success: bool = True
    summary: str = ""
    content: str = ""
    steps: list[AgentStep] = []
    total_duration_ms: int = 0
    mode: str = "auto"
    error: Optional[str] = None


class AgentExecutor:
    def __init__(self, engine, tools: RuntimeToolRegistry, memory_backend=None):
        self.engine = engine
        self.tools = tools
        self.max_steps = 12
        self.memory_backend = memory_backend

    def run(
        self,
        task: str,
        mode: AgentMode = AgentMode.AUTO,
        context: dict = None,
    ) -> AgentRunResult:
        start_time = time.time()
        context = context or {}
        resolved_mode = self._resolve_mode(task, mode)
        system_prompt = self._build_system_prompt(resolved_mode, context)

        messages = [{"role": "system", "content": system_prompt}]
        if context.get("history"):
            messages.extend(context["history"][-6:])
        messages.append({"role": "user", "content": task})

        steps: list[AgentStep] = []

        for turn in range(self.max_steps):
            step_start = time.time()
            step = AgentStep(step_number=turn + 1)

            try:
                raw = self.engine.generate(messages, temperature=0.3, max_tokens=2048)
            except Exception as e:
                step.thought = f"LLM error: {e}"
                step.observation = str(e)
                steps.append(step)
                break

            step.thought = raw[:500]

            tool_call = self._parse_tool_call(raw)
            if tool_call is None:
                messages.append({"role": "assistant", "content": raw})
                step.observation = "Final answer produced"
                steps.append(step)
                break

            tool_name, tool_args = tool_call
            step.tool = tool_name
            step.tool_input = tool_args

            result = self.tools.execute(tool_name, **tool_args)
            step.tool_result = result.content[:500]
            step.observation = f"Tool {tool_name} returned: {'OK' if result.success else 'FAILED'}"

            messages.append({"role": "assistant", "content": raw})
            messages.append({
                "role": "tool",
                "tool_call_id": tool_name,
                "content": json.dumps({"result": result.content[:2000], "success": result.success}),
            })

            step.duration_ms = int((time.time() - step_start) * 1000)
            steps.append(step)

            if result.success and "final" in raw.lower()[-200:]:
                break

            if not result.success and turn > 0:
                retry_prompt = f"The tool reported an error. Try a different approach.\nError: {result.error}"
                messages.append({"role": "user", "content": retry_prompt})

        total_duration = int((time.time() - start_time) * 1000)
        final_content = self._extract_final(messages)

        return AgentRunResult(
            success=all(s.tool_result is None or "FAILED" not in (s.observation or "") for s in steps),
            summary=self._summarize(steps),
            content=final_content,
            steps=steps,
            total_duration_ms=total_duration,
            mode=resolved_mode.value,
        )

    def _resolve_mode(self, task: str, preferred: AgentMode) -> AgentMode:
        if preferred != AgentMode.AUTO:
            return preferred
        code_keywords = ["create file", "write code", "implement", "refactor", "build", "project", "app", "fix bug"]
        assistant_keywords = ["call", "remind", "schedule", "open", "search", "what is", "who is"]
        task_lower = task.lower()
        if any(kw in task_lower for kw in code_keywords):
            return AgentMode.CODER
        if any(kw in task_lower for kw in assistant_keywords):
            return AgentMode.ASSISTANT
        return AgentMode.CHAT

    def _build_system_prompt(self, mode: AgentMode, context: dict) -> str:
        tools_desc = "\n".join(
            f"- {t.name}: {t.description}" for t in self.tools.list_tools()
        )
        base = f"""You are Ray, Mirai's reasoning engine. Your goal is to complete tasks by using available tools.

AVAILABLE TOOLS:
{tools_desc}

MODE: {mode.value}

RULES:
1. First, think about what needs to be done.
2. Choose the right tool and provide the correct parameters.
3. After each tool result, decide the next step.
4. When the task is complete, write "Final Answer:" followed by your summary.
5. Never make up tool results — always call the actual tool.
6. If a tool fails, try a different approach.

OUTPUT FORMAT:
When using a tool, output:
THOUGHT: your reasoning
TOOL: tool_name
PARAMS: {{"key": "value"}}

When done, output:
FINAL ANSWER: your summary
"""
        if mode == AgentMode.CODER:
            base += "\nYou are a coding agent. You can create, read, edit files, run commands, and use git. Build working solutions."
        elif mode == AgentMode.ASSISTANT:
            base += "\nYou are a phone assistant. You can manage tasks, reminders, contacts, and answer questions."
        elif mode == AgentMode.CHAT:
            base += "\nYou are a conversational agent. Answer questions helpfully. Avoid using tools unless necessary."

        if self.memory_backend:
            base += "\nYou have access to long-term memory. Use memory_recall to remember past context."

        return base

    def _parse_tool_call(self, text: str) -> Optional[tuple[str, dict]]:
        tool_match = re.search(r"TOOL:\s*(\w+)", text)
        params_match = re.search(r"PARAMS:\s*(\{.*?\})", text, re.DOTALL)
        final_match = re.search(r"FINAL ANSWER:", text)

        if final_match and not tool_match:
            return None

        if not tool_match:
            return None

        tool_name = tool_match.group(1)
        tool_args = {}
        if params_match:
            try:
                tool_args = json.loads(params_match.group(1))
            except json.JSONDecodeError:
                tool_args = {}

        if not self.tools.has(tool_name):
            return None

        return tool_name, tool_args

    def _extract_final(self, messages: list[dict]) -> str:
        for msg in reversed(messages):
            if msg["role"] == "assistant":
                content = msg.get("content", "")
                final_match = re.search(r"FINAL ANSWER:\s*(.*)", content, re.DOTALL)
                if final_match:
                    return final_match.group(1).strip()
                return content[-1000:]
        return ""

    def _summarize(self, steps: list[AgentStep]) -> str:
        tool_counts = {}
        for s in steps:
            if s.tool:
                tool_counts[s.tool] = tool_counts.get(s.tool, 0) + 1
        tools_used = ", ".join(f"{name}x{count}" for name, count in tool_counts.items())
        return f"Completed in {len(steps)} steps. Tools used: [{tools_used}]"
