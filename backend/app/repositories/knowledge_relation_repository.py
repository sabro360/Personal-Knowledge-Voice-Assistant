from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.knowledge_relation import KnowledgeRelation


class KnowledgeRelationRepository:
    """CRUD operations for KnowledgeRelation."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def create(
        self,
        source_id: int,
        target_id: int,
        relation_type: str,
        score: float,
    ) -> KnowledgeRelation:
        """Persist a new KnowledgeRelation and return it."""
        relation = KnowledgeRelation(
            source_knowledge_id=source_id,
            target_knowledge_id=target_id,
            relation_type=relation_type,
            score=score,
            created_at=datetime.now(timezone.utc),
        )
        self._db.add(relation)
        self._db.commit()
        self._db.refresh(relation)
        return relation

    def exists(self, source_id: int, target_id: int) -> bool:
        """Return True if a relation between the given IDs already exists."""
        stmt = select(KnowledgeRelation).where(
            KnowledgeRelation.source_knowledge_id == source_id,
            KnowledgeRelation.target_knowledge_id == target_id,
        )
        return self._db.scalar(stmt) is not None

    def list_all(self) -> list[KnowledgeRelation]:
        """Return all KnowledgeRelations ordered by created_at descending."""
        stmt = select(KnowledgeRelation).order_by(KnowledgeRelation.created_at.desc())
        return list(self._db.scalars(stmt).all())
