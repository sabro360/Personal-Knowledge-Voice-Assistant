from fastapi import FastAPI

app = FastAPI(
    title="Personal Knowledge Voice Assistant",
)


@app.get("/health")
def health_check() -> dict[str, str]:
    """Return server health status."""
    return {"status": "ok"}
