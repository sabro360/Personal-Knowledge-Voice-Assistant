from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.conversation_session import ConversationSession


class ConversationSessionRepository:
    """Repository for ConversationSession database operations."""

    def __init__(self, db: Session) -> None:
        """Initialize with a database session."""
        self._db = db

    def create(self, started_at: datetime) -> ConversationSession:
        """Create and persist a new ConversationSession."""
        cs = ConversationSession(started_at=started_at)
        self._db.add(cs)
        self._db.commit()
        self._db.refresh(cs)
        return cs

    def get_by_id(self, session_id: int) -> ConversationSession | None:
        """Return a ConversationSession by its ID, or None if not found."""
        return self._db.get(ConversationSession, session_id)

    def list(self) -> list[ConversationSession]:
        """Return all ConversationSessions ordered by started_at descending."""
        stmt = select(ConversationSession).order_by(ConversationSession.started_at.desc())
        return list(self._db.scalars(stmt).all())

    def finish(self, session_id: int, ended_at: datetime) -> ConversationSession | None:
        """Set ended_at on a ConversationSession. Returns updated session or None if not found."""
        cs = self.get_by_id(session_id)
        if cs is None:
            return None
        cs.ended_at = ended_at
        self._db.commit()
        self._db.refresh(cs)
        return cs
