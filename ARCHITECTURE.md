# Architecture — Ray Design

## Vision

Ray is a personal agentic AI system. Memory-first OS that can understand, remember, reason, and later act.

## Core Design

- **Language**: Python 3.11+
- **No external AI dependencies** — no OpenAI SDK, no LangChain, no HuggingFace
- **Storage**: Local file-based (JSONL for memory, plain text for config)
- **Interface**: Terminal only

## Architecture Priority

1. Memory correctness
2. Context retrieval
3. Reasoning
4. Reflection
5. Tools
6. Interface

## Module Layout

```
src/
├── memory/      — memory storage, recall, consolidation
├── context/     — context window management, retrieval
├── reason/      — reasoning engine, inference
├── reflect/     — self-reflection, update loop
├── tools/       — tool execution (future)
├── interface/   — terminal I/O, REPL
└── main.py      — entry point, event loop
```

Each module must work independently and not exceed 300 lines.

## Data Flow (Phase 1)

1. User sends text via terminal
2. Ray stores input in memory
3. Ray retrieves relevant memories
4. Ray builds context from memories + current input
5. Ray reasons and produces a response
6. Response is shown to user
7. Ray updates itself (reflection) after conversation

## Memory Correctness

Memories must be:
- Stored with timestamps and importance scores
- Retrievable by relevance (semantic or keyword)
- Consolidated periodically (merged, pruned, re-ranked)
- Never lost due to crashes (write-ahead / atomic writes)

## Future Directions

- Tool execution (code, file system, web)
- Voice interface
- GUI dashboard
- Plugin system
