# OPENCODE — AI Rules for Ray

This file governs how AI agents interact with the Ray codebase.

## Absolute Rules

1. Do not add features unless `TASKS.md` requests them.
2. Do not create frontend code.
3. Do not add voice.
4. Do not install unnecessary dependencies.
5. Do not rewrite architecture without permission.
6. Complete one module at a time.
7. After every change: explain what changed, test it, update `TASKS.md`.
8. If something is unclear — **ASK**. Do not guess.

## Workflow

- Always check `TASKS.md` before starting work.
- Each module must work independently.
- No file should exceed 300 lines.
- Keep files small, modular, and replaceable.

## Communication

- Keep explanations concise. Prefer code over commentary.
- If a task is ambiguous, ask the user before proceeding.
- Assume the user wants to learn — show how things fit together, not just that they work.
