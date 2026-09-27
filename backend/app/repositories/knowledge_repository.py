from __future__ import annotations

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.knowledge import Knowledge


class KnowledgeRepository:
    """Repository for Knowledge database operations."""

    def __init__(self, db: Session) -> None:
        """Initialize with a database session."""
        self._db = db

    def create(
        self,
        session_id: int,
        title: str | None = None,
        question: str | None = None,
        summary: str | None = None,
        answer: str | None = None,
        category: str | None = None,
    ) -> Knowledge:
        """Create and persist a new Knowledge item."""
        k = Knowledge(
            session_id=session_id,
            title=title,
            question=question,
            summary=summary,
            answer=answer,
            category=category,
        )
        self._db.add(k)
        self._db.commit()
        self._db.refresh(k)
        return k

    def get_by_id(self, knowledge_id: int) -> Knowledge | None:
        """Return a Knowledge item by its ID, or None if not found."""
        return self._db.get(Knowledge, knowledge_id)

    def list(self) -> list[Knowledge]:
        """Return all Knowledge items ordered by created_at descending."""
        stmt = select(Knowledge).order_by(Knowledge.created_at.desc())
        return list(self._db.scalars(stmt).all())

    def search(self, query: str) -> list[Knowledge]:
        """Return Knowledge items where title, question, summary, or answer match the query.

        Uses case-insensitive LIKE pattern matching ordered by created_at descending.
        """
        pattern = f"%{query}%"
        stmt = (
            select(Knowledge)
            .where(
                or_(
                    Knowledge.title.ilike(pattern),
                    Knowledge.question.ilike(pattern),
                    Knowledge.summary.ilike(pattern),
                    Knowledge.answer.ilike(pattern),
                )
            )
            .order_by(Knowledge.created_at.desc())
        )
        return list(self._db.scalars(stmt).all())

    def update(
        self,
        knowledge_id: int,
        title: str | None,
        question: str | None,
        summary: str | None,
        answer: str | None,
        category: str | None,
    ) -> Knowledge | None:
        """Update fields of an existing Knowledge item. Returns updated item or None if not found."""
        k = self.get_by_id(knowledge_id)
        if k is None:
            return None
        k.title = title
        k.question = question
        k.summary = summary
        k.answer = answer
        k.category = category
        self._db.commit()
        self._db.refresh(k)
        return k
