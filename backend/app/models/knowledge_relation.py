from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class KnowledgeRelation(Base):
    """Represents a similarity-based relation between two Knowledge items."""

    __tablename__ = "knowledge_relations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_knowledge_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("knowledge.id"), nullable=False
    )
    target_knowledge_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("knowledge.id"), nullable=False
    )
    relation_type: Mapped[str] = mapped_column(String, nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (
        UniqueConstraint(
            "source_knowledge_id",
            "target_knowledge_id",
            name="uq_knowledge_relation",
        ),
    )
