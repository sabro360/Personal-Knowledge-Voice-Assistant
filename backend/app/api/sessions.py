from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.conversation_session import ConversationSession
from app.repositories.conversation_session_repository import ConversationSessionRepository
from app.schemas.session import SessionResponse

router = APIRouter()


@router.post("", response_model=SessionResponse, status_code=201)
def create_session(db: Session = Depends(get_db)) -> ConversationSession:
    """Create a new conversation session."""
    repo = ConversationSessionRepository(db)
    return repo.create(started_at=datetime.now(timezone.utc))


@router.get("", response_model=list[SessionResponse])
def list_sessions(db: Session = Depends(get_db)) -> list[ConversationSession]:
    """Return all conversation sessions ordered by started_at descending."""
    repo = ConversationSessionRepository(db)
    return repo.list()


@router.get("/{session_id}", response_model=SessionResponse)
def get_session(session_id: int, db: Session = Depends(get_db)) -> ConversationSession:
    """Return a conversation session by ID."""
    repo = ConversationSessionRepository(db)
    cs = repo.get_by_id(session_id)
    if cs is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return cs
