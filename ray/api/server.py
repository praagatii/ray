import time
from contextlib import asynccontextmanager
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

from ray.brain.core import RayCore
from ray import config

core = RayCore()


@asynccontextmanager
async def lifespan(app: FastAPI):
    core.startup()
    yield


app = FastAPI(lifespan=lifespan)


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str
    timestamp: str


@app.get("/health")
def health():
    return {
        "status": "online",
        "brain": f"{config.MODEL_PROVIDER}/{config.OLLAMA_MODEL}"
    }


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    t0 = time.time()
    result = core.process_message(req.message, _timing=True)
    t_total = time.time() - t0
    print(f"\n=== TIMING ===")
    print(f"Total API response: {t_total:.1f}s")
    if "_timing" in result:
        for label, duration in result["_timing"].items():
            if isinstance(duration, (int, float)):
                print(f"{label}: {duration:.1f}s")
            else:
                print(f"{label}: {duration}")
    print(f"===============\n")
    return ChatResponse(
        response=result["ray_response"],
        timestamp=result["timestamp"]
    )


if __name__ == "__main__":
    print("Ray API running.")
    uvicorn.run(app, host="0.0.0.0", port=8000)
