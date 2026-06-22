from ray.identity.ray_identity import RAY_IDENTITY


def build_prompt(context: dict) -> str:
    user_msg = context.get("current_input", {}).get("text", "")
    user_identity = context.get("user_identity", {})
    memories = context.get("relevant_memories", [])

    parts = [RAY_IDENTITY]

    name = user_identity.get("name", "")
    if name:
        parts.append(f"User: {name}")

    if memories:
        mem_lines = [f"[{m['type']}] {m['content']}" for m in memories]
        parts.append(
            "Context:\n" + "\n".join(mem_lines)
        )

    projects = user_identity.get("projects", [])
    if projects:
        parts.append("Projects:\n" + "\n".join(f"- {p}" for p in projects))

    parts.append(f"Message: {user_msg}")

    return "\n\n".join(parts)
