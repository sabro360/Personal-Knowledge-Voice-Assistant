from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class KnowledgeKeyword(Base):
    """ORM model for the many-to-many association between Knowledge and Keyword."""

    __tablename__ = "knowledge_keywords"

    knowledge_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("knowledge.id"), primary_key=True
    )
    keyword_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("keywords.id"), primary_key=True
    )
