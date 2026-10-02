from datetime import datetime

from pydantic import BaseModel


class KnowledgeRelationResponse(BaseModel):
    """Response schema for a KnowledgeRelation."""

    id: int
    source_knowledge_id: int
    target_knowledge_id: int
    relation_type: str
    score: float
    created_at: datetime

    model_config = {"from_attributes": True}
