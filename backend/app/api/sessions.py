from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.db.database import get_db
from app.models.conversation_session import ConversationSession
from app.models.knowledge import Knowledge
from app.models.utterance import Utterance
from app.providers.errors import KnowledgeExtractionError
from app.providers.knowledge_model import KnowledgeModel
from app.providers.openai_knowledge_model import OpenAIKnowledgeModel
from app.repositories.conversation_session_repository import ConversationSessionRepository
from app.repositories.keyword_repository import KeywordRepository
from app.repositories.knowledge_repository import KnowledgeRepository
from app.repositories.utterance_repository import UtteranceRepository
from app.schemas.knowledge import KnowledgeResponse
from app.schemas.session import SessionResponse
from app.schemas.utterance import UtteranceCreate, UtteranceResponse
from app.services.knowledge_extraction_service import KnowledgeExtractionService

router = APIRouter()


def get_knowledge_model(settings: Settings = Depends(get_settings)) -> KnowledgeModel:
    """Return the configured KnowledgeModel instance."""
    if settings.openai_api_key:
        return OpenAIKnowledgeModel(api_key=settings.openai_api_key)
    raise HTTPException(status_code=503, detail="OpenAI API key not configured")


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


@router.post("/{session_id}/knowledge", response_model=KnowledgeResponse, status_code=201)
def generate_knowledge(
    session_id: int,
    db: Session = Depends(get_db),
    model: KnowledgeModel = Depends(get_knowledge_model),
) -> Knowledge:
    """Generate and persist a Knowledge item from a session's conversation."""
    session_repo = ConversationSessionRepository(db)
    if session_repo.get_by_id(session_id) is None:
        raise HTTPException(status_code=404, detail="Session not found")

    utterance_repo = UtteranceRepository(db)
    utterances = utterance_repo.list_by_session(session_id)

    service = KnowledgeExtractionService(
        db=db,
        knowledge_repo=KnowledgeRepository(db),
        keyword_repo=KeywordRepository(db),
        model=model,
    )
    try:
        return service.extract(session_id=session_id, utterances=utterances)
    except KnowledgeExtractionError:
        raise HTTPException(status_code=502, detail="Knowledge extraction failed")


@router.post("/{session_id}/finish", response_model=SessionResponse)
def finish_session(
    session_id: int,
    db: Session = Depends(get_db),
    model: KnowledgeModel = Depends(get_knowledge_model),
) -> ConversationSession:
    """Finish a conversation session and trigger synchronous knowledge generation."""
    repo = ConversationSessionRepository(db)
    cs = repo.finish(session_id, ended_at=datetime.now(timezone.utc))
    if cs is None:
        raise HTTPException(status_code=404, detail="Session not found")

    utterance_repo = UtteranceRepository(db)
    utterances = utterance_repo.list_by_session(session_id)
    service = KnowledgeExtractionService(
        db=db,
        knowledge_repo=KnowledgeRepository(db),
        keyword_repo=KeywordRepository(db),
        model=model,
    )
    try:
        service.extract(session_id=session_id, utterances=utterances)
    except KnowledgeExtractionError:
        pass  # Knowledge generation failure does not block session finish

    return cs
