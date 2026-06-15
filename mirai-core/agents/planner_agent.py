import json
import re
from typing import Optional
from models import Message, Role, AgentResult, AnalyzeRequest, AnalyzeResponse
from models.engine import LLMEngine
from tools.registry import ToolRegistry


class PlannerAgent:
    def __init__(self, engine: LLMEngine, tool_registry: Optional[ToolRegistry] = None):
        self.engine = engine
        self.tools = tool_registry or ToolRegistry()

    def analyze(self, req: AnalyzeRequest) -> AnalyzeResponse:
        system_prompt = """You are Mirai, an AI personal assistant that organizes unstructured thoughts into structured entities.

Available entity types:
- **projects**: Multi-step endeavors with status tracking
- **tasks**: Actionable items with priorities
- **learning**: Topics to study with progress tracking
- **personal**: Freeform journal entries and notes
- **ideas**: Creative sparks, optionally linked to projects

Rules:
1. Parse the user's natural language input and create/update/complete entities as needed
2. If input mentions completing something, mark it as completed
3. If input is about learning, create a learning entity with subtopics
4. Link related entities together using memory_links
5. Infer priority (1-5), deadlines, and dependencies where obvious
6. Return ONLY valid JSON matching the schema below

Response JSON Schema:
{
  "projects": [{"id": "", "title": "", "status": "", "progress": 0, "priority": null, "deadline": null}],
  "tasks": [{"id": "", "title": "", "completed": false, "priority": null, "deadline": null, "project_id": null, "tags": []}],
  "learning": [{"id": "", "topic": "", "progress": 0, "subtopics": [], "resources": []}],
  "personal": [{"id": "", "content": "", "created_at": ""}],
  "ideas": [{"id": "", "title": "", "notes": "", "project_id": null}],
  "memory_links": [{"source_type": "", "source_id": "", "target_type": "", "target_id": "", "link_type": "related_to"}],
  "focus": "Current primary focus derived from input",
  "reasoning": "Brief explanation of what was understood",
  "confidence": 85,
  "suggestions": ["Follow-up suggestion 1"],
  "what_changed": ["Description of what changed"],
  "next_action": "Single next recommended action",
  "blocked_by": []
}"""

        user_msg = json.dumps({
            "input": req.content,
            "current_state": req.state
        })

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_msg}
        ]

        raw = self.engine.generate(messages, response_format={"type": "json_object"})

        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            data = self._extract_json(raw)

        return AnalyzeResponse(
            projects=data.get("projects", []),
            tasks=data.get("tasks", []),
            learning=data.get("learning", []),
            personal=data.get("personal", []),
            ideas=data.get("ideas", []),
            memory_links=data.get("memory_links", []),
            focus=data.get("focus", ""),
            reasoning=data.get("reasoning", ""),
            confidence=data.get("confidence", 0.0),
            suggestions=data.get("suggestions", []),
            interpretation=data.get("interpretation", {}),
            reasoning_detail=data.get("reasoning_detail", {}),
            what_changed=data.get("what_changed", []),
            next_action=data.get("next_action", ""),
            blocked_by=data.get("blocked_by", [])
        )

    def _extract_json(self, text: str) -> dict:
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
        return {}

    def chat(self, message: str, history: list[dict] = None) -> AgentResult:
        messages = [
            {"role": "system", "content": "You are Mirai, a helpful AI assistant. Be concise and helpful."}
        ]
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": message})

        response = self.engine.generate(messages)
        return AgentResult(content=response, turns=1)
