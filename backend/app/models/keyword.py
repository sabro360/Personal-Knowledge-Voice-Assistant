from sqlalchemy import Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class Keyword(Base):
    """ORM model for a keyword tag associated with knowledge items."""

    __tablename__ = "keywords"
    __table_args__ = (UniqueConstraint("name", name="uq_keywords_name"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
