import uuid
from datetime import datetime, timezone


class InputProcessor:
    def process(self, raw_text: str) -> dict:
        return {
            "id": str(uuid.uuid4()),
            "text": raw_text.strip(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": "conversation",
            "metadata": {}
        }


if __name__ == "__main__":
    proc = InputProcessor()
    result = proc.process("  Hello from Ray  ")
    print(result)
