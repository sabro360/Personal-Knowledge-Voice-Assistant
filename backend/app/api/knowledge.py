from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.knowledge import Knowledge
from app.repositories.knowledge_repository import KnowledgeRepository
from app.schemas.knowledge import KnowledgeResponse

router = APIRouter()


@router.get("", response_model=list[KnowledgeResponse])
def list_knowledge(db: Session = Depends(get_db)) -> list[Knowledge]:
    """Return all knowledge items ordered by created_at descending."""
    repo = KnowledgeRepository(db)
    return repo.list()
