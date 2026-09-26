from fastapi import FastAPI

from app.api.knowledge import router as knowledge_router
from app.api.sessions import router as sessions_router

app = FastAPI(
    title="Personal Knowledge Voice Assistant",
)

app.include_router(knowledge_router, prefix="/knowledge", tags=["knowledge"])
app.include_router(sessions_router, prefix="/sessions", tags=["sessions"])


@app.get("/health")
def health_check() -> dict[str, str]:
    """Return server health status."""
    return {"status": "ok"}
