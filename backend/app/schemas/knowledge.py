from datetime import datetime

from pydantic import BaseModel, ConfigDict


class KnowledgeResponse(BaseModel):
    """API response schema for a Knowledge item."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    session_id: int
    title: str | None
    question: str | None
    summary: str | None
    answer: str | None
    category: str | None
    created_at: datetime
    updated_at: datetime
