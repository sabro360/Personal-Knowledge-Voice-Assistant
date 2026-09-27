from fastapi import APIRouter, Depends, HTTPException
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


@router.get("/{knowledge_id}", response_model=KnowledgeResponse)
def get_knowledge(knowledge_id: int, db: Session = Depends(get_db)) -> Knowledge:
    """Return a single knowledge item by ID."""
    repo = KnowledgeRepository(db)
    knowledge = repo.get_by_id(knowledge_id)
    if knowledge is None:
        raise HTTPException(status_code=404, detail="Knowledge not found")
    return knowledge
