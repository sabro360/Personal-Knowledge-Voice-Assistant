from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class KnowledgeResponse(BaseModel):
    """API response schema for a Knowledge item (list view)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    session_id: int
    title: str | None
    question: str | None
    summary: str | None
    answer: str | None
    category: str | None
    related_questions: list[str] | None
    created_at: datetime
    updated_at: datetime


class KnowledgeDetailResponse(KnowledgeResponse):
    """API response schema for a Knowledge item with keywords (detail view)."""

    keywords: list[str]


class KnowledgeToolRequest(BaseModel):
    """Request body for the knowledge search tool endpoint."""

    query: str = Field(min_length=1)


class KnowledgeToolResult(BaseModel):
    """A single knowledge item returned by the search tool (AI-facing fields only)."""

    title: str | None
    question: str | None
    summary: str | None
    answer: str | None
    category: str | None


class KnowledgeToolResponse(BaseModel):
    """Response from the knowledge search tool endpoint."""

    results: list[KnowledgeToolResult]
    count: int
