from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.conversation_session import ConversationSession
from app.models.utterance import Utterance
from app.repositories.conversation_session_repository import ConversationSessionRepository
from app.repositories.utterance_repository import UtteranceRepository
from app.schemas.session import SessionResponse
from app.schemas.utterance import UtteranceCreate, UtteranceResponse

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


@router.post("/{session_id}/utterances", response_model=UtteranceResponse, status_code=201)
def add_utterance(
    session_id: int,
    body: UtteranceCreate,
    db: Session = Depends(get_db),
) -> Utterance:
    """Add an utterance to a conversation session."""
    session_repo = ConversationSessionRepository(db)
    if session_repo.get_by_id(session_id) is None:
        raise HTTPException(status_code=404, detail="Session not found")

    utterance_repo = UtteranceRepository(db)
    existing = utterance_repo.list_by_session(session_id)
    sequence_number = len(existing) + 1

    return utterance_repo.create(
        session_id=session_id,
        speaker=body.speaker,
        text=body.text,
        timestamp=datetime.now(timezone.utc),
        sequence_number=sequence_number,
    )


@router.get("/{session_id}/utterances", response_model=list[UtteranceResponse])
def list_utterances(session_id: int, db: Session = Depends(get_db)) -> list[Utterance]:
    """Return all utterances for a session ordered by sequence_number ascending."""
    session_repo = ConversationSessionRepository(db)
    if session_repo.get_by_id(session_id) is None:
        raise HTTPException(status_code=404, detail="Session not found")

    utterance_repo = UtteranceRepository(db)
    return utterance_repo.list_by_session(session_id)


@router.post("/{session_id}/finish", response_model=SessionResponse)
def finish_session(session_id: int, db: Session = Depends(get_db)) -> ConversationSession:
    """Finish a conversation session by setting ended_at."""
    repo = ConversationSessionRepository(db)
    cs = repo.finish(session_id, ended_at=datetime.now(timezone.utc))
    if cs is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return cs
