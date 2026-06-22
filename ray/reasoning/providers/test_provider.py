from ray.reasoning.providers.base import BaseProvider


class TestProvider(BaseProvider):
    def info(self) -> str:
        return "TestProvider (no model)"

    def think(self, context: dict) -> dict:
        response = self._generate_response(context)
        return {
            "response": response,
            "reasoning_summary": self._reasoning_summary(context),
            "model_used": "test"
        }

    def _generate_response(self, context: dict) -> str:
        user_msg = context.get("current_input", {}).get("text", "").lower()
        memories = context.get("relevant_memories", [])

        if not memories:
            return "I'm listening. Tell me more about that."

        problems = [m for m in memories if m["type"] == "problem"]
        projects = [m for m in memories if m["type"] == "project"]

        def project_for_problem(problem: dict) -> dict | None:
            p_tags = set(problem.get("tags", []))
            for proj in projects:
                proj_lower = proj["content"].lower()
                for tag in p_tags:
                    if tag.lower() in proj_lower:
                        return proj
                first_word = proj["content"].split(":")[0].split(" ")[0].lower()
                if first_word in p_tags:
                    return proj
            return None

        if "stuck" in user_msg or "not working" in user_msg or "isn't working" in user_msg:
            if problems:
                p = problems[0]
                related = project_for_problem(p)
                if related:
                    return (
                        f"Looks like this might be connected to {related['content']} "
                        f"and {p['content'].lower()}… "
                        f"Let's talk through what's going on."
                    )
                return (
                    f"I remember {p['content']} has been on your mind. "
                    f"Let's work through it together. What's the specific issue?"
                )
            if projects:
                return (
                    f"I remember you're working on {projects[0]['content']}. "
                    f"What specifically is challenging right now?"
                )
            top = memories[0]
            return (
                f"I remember {top['content']} has been on your mind. "
                f"Let's work through it together."
            )

        if "mugen" in user_msg:
            return (
                f"About Mugen — I remember that's your creative studio. "
                f"How are things going with it?"
            )

        if "building" in user_msg or "working on" in user_msg or "project" in user_msg or "make" in user_msg:
            if projects:
                names = [p["content"] for p in projects]
                return (
                    f"You're working on: {' and '.join(names)}. "
                    f"What would you like to focus on?"
                )

        top = memories[0]
        return (
            f"I recall {top['content']} is relevant here. "
            f"Tell me more about what you're thinking."
        )

    def _reasoning_summary(self, context: dict) -> str:
        memories = context.get("relevant_memories", [])
        if not memories:
            return "No relevant memories to reference."
        return f"Referenced top memory: [{memories[0]['type']}] {memories[0]['content']}"
