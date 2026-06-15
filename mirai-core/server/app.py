import json
import uuid
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from models import (
    AnalyzeRequest, AnalyzeResponse, Message, Role, Entity, EntityType,
    MemoryItem, AgentResult, ToolSpec
)
from models.engine import LLMEngine, get_engine, has_api_key, resolve_engine_info
from agents.planner_agent import PlannerAgent
from agents.memory_agent import MemoryAgent
from agents.action_agent import ActionAgent
from memory.short_term import ShortTermMemory
from memory.long_term import LongTermMemory
from tools.registry import ToolRegistry
from tools.apps import OpenAppTool, ListAppsTool
from tools.calendar import CalendarTool
from tools.reminders import ReminderTool
from tools.files import FileSearchTool, FileReadTool
from tools.contacts import ContactLookupTool
from tools.notifications import NotificationTool
from tools.calculator_tool import CalculatorTool
from tools.web_search_tool import WebSearchTool
from tools.weather_tool import WeatherTool
from voice.stt import SpeechToText
from voice.tts import TextToSpeech
from forge import AgentExecutor, AgentMode
from forge.tool_registry import RuntimeToolRegistry
from forge.shell_tool import ShellTool, PythonEvalTool
from forge.file_tool import FileReadTool, FileWriteTool, FileEditTool, FileListTool, set_allowed_workspaces
from forge.git_tool import GitTool, GitDiffTool
from forge.android_tool import (
    AndroidBuildTool, AndroidAdbTool,
    AndroidNotificationTool, AndroidIntentTool,
    AndroidAppsTool, AndroidContactsTool, AndroidCalendarTool,
)
from forge.memory_tool import MemoryStoreTool, MemoryRecallTool, MemoryRecentTool
from memory.graph import GraphMemory
from echo import EchoTranscriber, EchoSpeaker


class MiraiCore:
    def __init__(self):
        self.engine: LLMEngine = get_engine()
        self.stm = ShortTermMemory()
        self.ltm = LongTermMemory()
        self.nexus = GraphMemory()
        self.echo_stt = EchoTranscriber()
        self.echo_tts = EchoSpeaker()

        self.tools = ToolRegistry()
        self._register_tools()
        self._init_forge()

        self.planner = PlannerAgent(self.engine, self.tools)
        self.memory_agent = MemoryAgent(self.engine, self.stm, self.ltm)
        self.action_agent = ActionAgent(self.engine, self.tools)
        self.stt = SpeechToText()
        self.tts = TextToSpeech()

        import os
        self.config = {
            "engine": self.engine.name(),
            "model": os.getenv(f"{self.engine.name().upper()}_MODEL", "default"),
            "wake_word": "hey mirai",
            "voice_enabled": True,
        }

    def _init_forge(self):
        project_root = Path(__file__).parent.parent.resolve()
        set_allowed_workspaces([str(project_root)])

        self.forge_tools = RuntimeToolRegistry()
        self.forge_tools.register(ShellTool())
        self.forge_tools.register(PythonEvalTool())
        self.forge_tools.register(FileReadTool())
        self.forge_tools.register(FileWriteTool())
        self.forge_tools.register(FileEditTool())
        self.forge_tools.register(FileListTool())
        self.forge_tools.register(GitTool())
        self.forge_tools.register(GitDiffTool())
        self.forge_tools.register(AndroidBuildTool())
        self.forge_tools.register(AndroidAdbTool())
        self.forge_tools.register(AndroidNotificationTool())
        self.forge_tools.register(AndroidIntentTool())
        self.forge_tools.register(AndroidAppsTool())
        self.forge_tools.register(AndroidContactsTool())
        self.forge_tools.register(AndroidCalendarTool())
        store = MemoryStoreTool(memory_backend=self.ltm)
        recall = MemoryRecallTool(memory_backend=self.ltm)
        recent = MemoryRecentTool(memory_backend=self.ltm)
        self.forge_tools.register(store)
        self.forge_tools.register(recall)
        self.forge_tools.register(recent)
        self.forge_executor = AgentExecutor(self.engine, self.forge_tools, memory_backend=self.ltm)

    def _register_tools(self):
        self.tools.register(OpenAppTool())
        self.tools.register(ListAppsTool())
        self.tools.register(CalendarTool())
        self.tools.register(ReminderTool())
        self.tools.register(FileSearchTool())
        self.tools.register(FileReadTool())
        self.tools.register(ContactLookupTool())
        self.tools.register(NotificationTool())
        self.tools.register(CalculatorTool())
        self.tools.register(WebSearchTool())
        self.tools.register(WeatherTool())

    def set_engine(self, engine_type: str):
        self.engine = get_engine(engine_type)
        self.planner = PlannerAgent(self.engine, self.tools)
        self.memory_agent = MemoryAgent(self.engine, self.stm, self.ltm)
        self.action_agent = ActionAgent(self.engine, self.tools)
        self.config["engine"] = engine_type

    def process_thought(self, content: str, state: dict = None) -> AnalyzeResponse:
        req = AnalyzeRequest(content=content, state=state or {})
        response = self.planner.analyze(req)

        self.memory_agent.store_conversation(
            user_input=content,
            response=json.dumps(response.dict()),
            metadata={"type": "thought_analysis"}
        )

        return response

    def chat(self, message: str, history: list[dict] = None) -> AgentResult:
        result = self.planner.chat(message, history)
        self.memory_agent.store_conversation(message, result.content)
        return result

    def get_memories(self, query: str = "", top_k: int = 10) -> list[dict]:
        if query:
            return self.memory_agent.recall(query, top_k)
        return self.ltm.get_recent(top_k)

    def execute_tool(self, tool_name: str, params: dict = None) -> dict:
        result = self.tools.execute(tool_name, **(params or {}))
        return {"content": result.content, "success": result.success, "error": result.error}


def create_app() -> FastAPI:
    app = FastAPI(title="Mirai Core API", version="1.0.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    core = MiraiCore()

    @app.get("/health")
    def health():
        info = resolve_engine_info()
        return {"status": "ok", "engine": info["engine"], "model": info["model"]}

    @app.post("/api/analyze", response_model=AnalyzeResponse)
    def analyze(req: AnalyzeRequest):
        try:
            return core.process_thought(req.content, req.state)
        except Exception as e:
            if not has_api_key():
                msg = "Set OPENROUTER_API_KEY in mirai-core/.env to enable AI"
            else:
                msg = f"AI error: {str(e)[:100]}"
            return AnalyzeResponse(
                focus="Mirai ready",
                reasoning=msg,
                confidence=0,
                suggestions=["Check your API key in .env file"]
            )

    @app.post("/api/chat")
    def chat(req: dict):
        message = req.get("message", "")
        history = req.get("history", [])
        try:
            result = core.chat(message, history)
            return {"content": result.content, "turns": result.turns, "success": True}
        except Exception as e:
            err_msg = str(e)[:150]
            if not has_api_key():
                msg = "To use Mirai, set OPENROUTER_API_KEY in mirai-core/.env file. Get one at https://openrouter.ai/keys"
            else:
                msg = f"AI error: {err_msg}"
            return {"content": msg, "turns": 0, "success": False}

    @app.post("/api/memory/search")
    def memory_search(req: dict):
        query = req.get("query", "")
        top_k = req.get("top_k", 10)
        return {"results": core.get_memories(query, top_k)}

    @app.get("/api/memory/stats")
    def memory_stats():
        return core.ltm.get_stats()

    @app.post("/api/memory/store")
    def memory_store(req: dict):
        core.ltm.store(
            content=req.get("content", ""),
            source=req.get("source", "api"),
            metadata=req.get("metadata", {})
        )
        return {"status": "stored"}

    @app.post("/api/memory/summarize")
    def memory_summarize():
        summary = core.memory_agent.summarize_memory()
        return {"summary": summary}

    @app.post("/api/tools/execute")
    def tool_execute(req: dict):
        return core.execute_tool(req.get("name", ""), req.get("params", {}))

    @app.get("/api/tools/list")
    def tool_list():
        return {"tools": [t.dict() for t in core.tools.list_tools()]}

    @app.post("/api/voice/stt")
    def voice_stt():
        text = core.stt.listen_from_mic(5)
        return {"text": text}

    @app.post("/api/voice/tts")
    def voice_tts(req: dict):
        text = req.get("text", "")
        core.tts.speak_async(text)
        return {"status": "speaking"}

    @app.post("/api/config")
    def set_config(req: dict):
        if "engine" in req:
            core.set_engine(req["engine"])
        if "model" in req:
            core.config["model"] = req["model"]
        return {"status": "configured", "config": core.config}

    @app.get("/api/config")
    def get_config():
        return core.config

    @app.post("/api/memory/clear")
    def memory_clear():
        core.stm.clear()
        core.ltm.clear()
        return {"status": "cleared"}

    @app.post("/api/conversation")
    def conversation(req: dict):
        message = req.get("message", "")
        state = req.get("state", {})

        try:
            thought_result = core.process_thought(message, state)
            memory_context = core.get_memories(message, 5)
            response = {
                "analysis": thought_result.dict(),
                "memory_context": memory_context,
                "config": core.config,
                "success": True
            }
        except Exception as e:
            if not has_api_key():
                msg = "Set OPENROUTER_API_KEY in mirai-core/.env"
            else:
                msg = f"AI error: {str(e)[:100]}"
            response = {
                "analysis": {
                    "focus": "Mirai ready",
                    "reasoning": msg,
                    "confidence": 0,
                    "projects": [], "tasks": [], "learning": [], "personal": [], "ideas": [],
                    "memory_links": [], "suggestions": [], "what_changed": [],
                    "next_action": "", "blocked_by": [],
                    "interpretation": {}, "reasoning_detail": {}
                },
                "memory_context": [],
                "config": core.config,
                "success": False
            }
        return response

    @app.post("/api/agent/run")
    def agent_run(req: dict):
        task = req.get("task", "")
        mode_str = req.get("mode", "auto")
        context = req.get("context", {})

        if not task:
            return {"success": False, "error": "No task provided", "content": "", "steps": []}

        try:
            mode = AgentMode(mode_str)
        except ValueError:
            mode = AgentMode.AUTO

        try:
            result = core.forge_executor.run(task=task, mode=mode, context=context)
            return result.dict()
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "content": "",
                "summary": "",
                "steps": [],
                "total_duration_ms": 0,
                "mode": mode_str,
            }

    @app.get("/api/agent/tools")
    def agent_tools():
        return {"tools": [t.dict() for t in core.forge_tools.list_tools()]}

    # --- Nexus: Memory Graph ---

    @app.post("/api/nexus/nodes")
    def nexus_add_node(req: dict):
        node_type = req.get("type", "note")
        name = req.get("name", "")
        properties = req.get("properties", {})
        if not name:
            return {"error": "Name is required", "success": False}
        node = core.nexus.add_node(node_type, name, properties)
        return {"node": node, "success": True}

    @app.get("/api/nexus/nodes/{node_id}")
    def nexus_get_node(node_id: str):
        node = core.nexus.get_node(node_id)
        if not node:
            return {"error": "Node not found", "success": False}
        return {"node": node, "success": True}

    @app.delete("/api/nexus/nodes/{node_id}")
    def nexus_delete_node(node_id: str):
        ok = core.nexus.delete_node(node_id)
        return {"success": ok}

    @app.get("/api/nexus/nodes")
    def nexus_list_nodes(type: str = "", query: str = ""):
        nodes = core.nexus.query_nodes(type or None, query)
        return {"nodes": nodes, "total": len(nodes)}

    @app.post("/api/nexus/edges")
    def nexus_add_edge(req: dict):
        source_id = req.get("source_id", "")
        target_id = req.get("target_id", "")
        edge_type = req.get("type", "related_to")
        properties = req.get("properties", {})
        try:
            edge = core.nexus.add_edge(source_id, target_id, edge_type, properties)
            return {"edge": edge, "success": True}
        except ValueError as e:
            return {"error": str(e), "success": False}

    @app.get("/api/nexus/connections/{node_id}")
    def nexus_connections(node_id: str):
        return core.nexus.get_connections(node_id)

    @app.get("/api/nexus/graph")
    def nexus_graph():
        return core.nexus.get_graph()

    @app.get("/api/nexus/search")
    def nexus_search(query: str = ""):
        return {"results": core.nexus.search(query)}

    @app.get("/api/nexus/stats")
    def nexus_stats():
        return core.nexus.get_stats()

    # --- Echo: Voice System ---

    @app.post("/api/echo/transcribe")
    def echo_transcribe(req: dict):
        audio_b64 = req.get("audio", "")
        duration = req.get("duration", 5)
        if audio_b64:
            import base64
            audio_data = base64.b64decode(audio_b64)
            text = core.echo_stt.transcribe(audio_data)
        else:
            phrases = core.echo_stt.listen_continuous(duration, 1)
            text = " ".join(phrases)
        if text.strip():
            core.nexus.add_node("thought", text, {"source": "echo"})
        return {"text": text}

    @app.post("/api/echo/speak")
    def echo_speak(req: dict):
        text = req.get("text", "")
        if text:
            core.echo_tts.speak_async(text)
            return {"status": "speaking", "text": text}
        return {"error": "No text provided"}

    @app.post("/api/echo/thought")
    def echo_save_thought(req: dict):
        text = req.get("text", "")
        if text:
            node = core.nexus.add_node("thought", text, {"source": "echo"})
            return {"saved": True, "node": node}
        return {"error": "No text", "saved": False}

    return app
