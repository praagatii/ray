from enum import Enum
from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class Role(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class Message(BaseModel):
    role: Role
    content: str
    tool_call_id: Optional[str] = None
    name: Optional[str] = None


class ToolCall(BaseModel):
    name: str
    arguments: dict


class ToolResult(BaseModel):
    tool_name: str
    content: str
    success: bool = True
    error: Optional[str] = None


class AgentResult(BaseModel):
    content: str
    tool_results: list[ToolResult] = []
    turns: int = 1


class EntityType(str, Enum):
    PROJECT = "project"
    TASK = "task"
    LEARNING = "learning"
    PERSONAL = "personal"
    IDEA = "idea"


class Entity(BaseModel):
    id: str
    type: EntityType
    title: str
    content: Optional[str] = None
    status: Optional[str] = None
    completed: bool = False
    priority: Optional[int] = None
    deadline: Optional[str] = None
    tags: list[str] = []
    created_at: str = ""


class AnalyzeRequest(BaseModel):
    content: str
    state: dict = {}


class AnalyzeResponse(BaseModel):
    projects: list[dict] = []
    tasks: list[dict] = []
    learning: list[dict] = []
    personal: list[dict] = []
    ideas: list[dict] = []
    memory_links: list[dict] = []
    focus: str = ""
    reasoning: str = ""
    confidence: float = 0.0
    suggestions: list[str] = []
    interpretation: dict = {}
    reasoning_detail: dict = {}
    what_changed: list[str] = []
    next_action: str = ""
    blocked_by: list[str] = []


class MemoryItem(BaseModel):
    id: str
    content: str
    source: str
    metadata: dict = {}
    timestamp: str = ""


class ToolSpec(BaseModel):
    name: str
    description: str
    parameters: dict = {}
