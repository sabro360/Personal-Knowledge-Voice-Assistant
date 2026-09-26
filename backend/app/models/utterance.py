import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class SpeakerType(str, enum.Enum):
    """Speaker role in a conversation utterance."""

    user = "user"
    assistant = "assistant"
    system = "system"


class Utterance(Base):
    """ORM model for a single utterance within a conversation session."""

    __tablename__ = "utterances"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("conversation_sessions.id"), nullable=False
    )
    speaker: Mapped[SpeakerType] = mapped_column(
        Enum(SpeakerType, name="speaker_type"), nullable=False
    )
    text: Mapped[str] = mapped_column(Text, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    sequence_number: Mapped[int] = mapped_column(Integer, nullable=False)
