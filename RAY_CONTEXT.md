# Ray Project Context

Ray is a personal AI second brain.

IMPORTANT:
The Android app is ONLY a client.

Do not build AI inside Android.

Existing architecture:

User
 ↓
Android App
 ↓
HTTP API
 ↓
Ray Core (Python)
 ↓
Ollama qwen2.5:7b


Ray backend already exists:

Location:
C:\Users\hp\Desktop\ray2


Completed backend:

- RayCore
- memory system
- identity layer
- reflection
- Ollama provider
- qwen2.5:7b
- FastAPI server


Current API:

POST /chat

Input:
{
 "message":"hello"
}

Output:
{
 "response":"Ray reply"
}


GET /health

Output:
{
 "status":"online",
 "brain":"ollama/qwen2.5:7b"
}


Rules:

NEVER:
- create another AI assistant
- add OpenAI/Gemini
- create memory storage
- create chatbot logic

Android responsibilities ONLY:

- UI
- send user messages
- display Ray responses
- voice input later
- voice output later


Current phase:

Phase 2.2

Goal:

Create basic text chat Android app connected to Ray API.
