from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.utterance import SpeakerType, Utterance


class UtteranceRepository:
    """Repository for Utterance database operations."""

    def __init__(self, db: Session) -> None:
        """Initialize with a database session."""
        self._db = db

    def create(
        self,
        session_id: int,
        speaker: SpeakerType,
        text: str,
        timestamp: datetime,
        sequence_number: int,
    ) -> Utterance:
        """Create and persist a new Utterance."""
        utt = Utterance(
            session_id=session_id,
            speaker=speaker,
            text=text,
            timestamp=timestamp,
            sequence_number=sequence_number,
        )
        self._db.add(utt)
        self._db.commit()
        self._db.refresh(utt)
        return utt

    def list_by_session(self, session_id: int) -> list[Utterance]:
        """Return all Utterances for a session ordered by sequence_number ascending."""
        stmt = (
            select(Utterance)
            .where(Utterance.session_id == session_id)
            .order_by(Utterance.sequence_number.asc())
        )
        return list(self._db.scalars(stmt).all())
