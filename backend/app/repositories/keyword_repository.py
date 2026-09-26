from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.keyword import Keyword
from app.models.knowledge_keyword import KnowledgeKeyword


class KeywordRepository:
    """Repository for Keyword database operations."""

    def __init__(self, db: Session) -> None:
        """Initialize with a database session."""
        self._db = db

    def get_or_create(self, name: str) -> Keyword:
        """Return existing Keyword with the given name, or create and return a new one."""
        stmt = select(Keyword).where(Keyword.name == name)
        k = self._db.scalars(stmt).first()
        if k is not None:
            return k
        k = Keyword(name=name)
        self._db.add(k)
        self._db.commit()
        self._db.refresh(k)
        return k

    def list_for_knowledge(self, knowledge_id: int) -> list[Keyword]:
        """Return all Keywords associated with the given knowledge_id, ordered by name ascending."""
        stmt = (
            select(Keyword)
            .join(KnowledgeKeyword, Keyword.id == KnowledgeKeyword.keyword_id)
            .where(KnowledgeKeyword.knowledge_id == knowledge_id)
            .order_by(Keyword.name.asc())
        )
        return list(self._db.scalars(stmt).all())
