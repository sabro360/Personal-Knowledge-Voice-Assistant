from pydantic import BaseModel


class KnowledgeExtraction(BaseModel):
    """Structured output schema for a single knowledge item extracted from a conversation."""

    title: str
    question: str | None = None
    summary: str
    answer: str
    category: str
    keywords: list[str]
    related_questions: list[str] = []


class KnowledgeExtractionList(BaseModel):
    """Wrapper for a list of knowledge items extracted from a conversation."""

    items: list[KnowledgeExtraction]
