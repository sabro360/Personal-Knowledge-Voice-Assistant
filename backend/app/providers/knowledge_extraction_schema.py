from pydantic import BaseModel


class KnowledgeExtraction(BaseModel):
    """Structured output schema for knowledge extracted from a conversation."""

    title: str
    question: str
    summary: str
    answer: str
    category: str
    keywords: list[str]
