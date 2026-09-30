from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.knowledge import Knowledge
from app.repositories.keyword_repository import KeywordRepository
from app.repositories.knowledge_repository import KnowledgeRepository
from app.schemas.knowledge import (
    KnowledgeDetailResponse,
    KnowledgeResponse,
    KnowledgeToolRequest,
    KnowledgeToolResponse,
    KnowledgeToolResult,
)
from app.services.knowledge_search_service import KnowledgeSearchService

router = APIRouter()


@router.get("", response_model=list[KnowledgeResponse])
def list_knowledge(db: Session = Depends(get_db)) -> list[Knowledge]:
    """Return all knowledge items ordered by created_at descending."""
    repo = KnowledgeRepository(db)
    return repo.list()


@router.get("/search", response_model=list[KnowledgeResponse])
def search_knowledge(
    q: str = Query(min_length=1),
    db: Session = Depends(get_db),
) -> list[Knowledge]:
    """Search knowledge items by title, question, summary, or answer."""
    repo = KnowledgeRepository(db)
    return repo.search(q)


@router.post("/search_tool", response_model=KnowledgeToolResponse, status_code=200)
def search_knowledge_tool(
    body: KnowledgeToolRequest,
    db: Session = Depends(get_db),
) -> KnowledgeToolResponse:
    """Execute knowledge search as an AI tool call."""
    service = KnowledgeSearchService(knowledge_repo=KnowledgeRepository(db))
    knowledge_items = service.search(body.query)
    results = [
        KnowledgeToolResult(
            title=k.title,
            question=k.question,
            summary=k.summary,
            answer=k.answer,
            category=k.category,
        )
        for k in knowledge_items
    ]
    return KnowledgeToolResponse(results=results, count=len(results))


@router.get("/{knowledge_id}", response_model=KnowledgeDetailResponse)
def get_knowledge(
    knowledge_id: int, db: Session = Depends(get_db)
) -> KnowledgeDetailResponse:
    """Return a single knowledge item with keywords by ID."""
    repo = KnowledgeRepository(db)
    knowledge = repo.get_by_id(knowledge_id)
    if knowledge is None:
        raise HTTPException(status_code=404, detail="Knowledge not found")
    keyword_repo = KeywordRepository(db)
    keyword_names = [kw.name for kw in keyword_repo.list_for_knowledge(knowledge_id)]
    return KnowledgeDetailResponse(
        id=knowledge.id,
        session_id=knowledge.session_id,
        title=knowledge.title,
        question=knowledge.question,
        summary=knowledge.summary,
        answer=knowledge.answer,
        category=knowledge.category,
        related_questions=knowledge.related_questions,
        created_at=knowledge.created_at,
        updated_at=knowledge.updated_at,
        keywords=keyword_names,
    )
