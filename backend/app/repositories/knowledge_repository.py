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
        related_questions: list[str] | None = None,
    ) -> Knowledge:
        """Create and persist a new Knowledge item."""
        k = Knowledge(
            session_id=session_id,
            title=title,
            question=question,
            summary=summary,
            answer=answer,
            category=category,
            related_questions=related_questions,
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

    def list_by_session(self, session_id: int) -> list[Knowledge]:
        """Return Knowledge items for the given session ordered by created_at ascending."""
        stmt = (
            select(Knowledge)
            .where(Knowledge.session_id == session_id)
            .order_by(Knowledge.created_at.asc())
        )
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

    def update_embedding(self, knowledge_id: int, embedding: list[float]) -> None:
        """Update the embedding vector of a Knowledge item."""
        k = self.get_by_id(knowledge_id)
        if k is None:
            return
        k.embedding = embedding
        self._db.commit()

    def semantic_search(
        self, embedding: list[float], limit: int = 10
    ) -> list[Knowledge]:
        """Return Knowledge items ordered by cosine similarity to the given embedding.

        Uses pgvector <=> (cosine distance) operator. Returns empty list on
        non-PostgreSQL dialects or when no items have embeddings.
        """
        if self._db.bind.dialect.name != "postgresql":  # type: ignore[union-attr]
            return []
        stmt = (
            select(Knowledge)
            .where(Knowledge.embedding.is_not(None))
            .order_by(Knowledge.embedding.op("<=>")(embedding))
            .limit(limit)
        )
        return list(self._db.scalars(stmt).all())

    def find_similar(
        self,
        knowledge_id: int,
        threshold: float = 0.25,
        limit: int = 5,
    ) -> list[tuple[Knowledge, float]]:
        """Return Knowledge items within cosine distance threshold of the given item.

        Returns list of (Knowledge, similarity_score) where similarity_score = 1 - distance.
        Returns empty list on non-PostgreSQL dialects or if the target has no embedding.
        """
        if self._db.bind.dialect.name != "postgresql":  # type: ignore[union-attr]
            return []
        k = self.get_by_id(knowledge_id)
        if k is None or k.embedding is None:
            return []
        distance_col = Knowledge.embedding.op("<=>")(k.embedding).label("distance")
        stmt = (
            select(Knowledge, distance_col)
            .where(Knowledge.embedding.is_not(None))
            .where(Knowledge.id != knowledge_id)
            .where(distance_col <= threshold)
            .order_by(distance_col)
            .limit(limit)
        )
        rows = self._db.execute(stmt).all()
        return [(row[0], 1.0 - row[1]) for row in rows]

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
