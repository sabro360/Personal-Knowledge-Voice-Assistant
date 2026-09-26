from datetime import datetime, timezone

from fastapi import APIRouter, Depends
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
