from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from typing import List, Optional
from app.models.schemas import KnowledgeItemCreate, KnowledgeItemResponse
from app.models.models import KnowledgeItem
from app.services.database import get_db

router = APIRouter()


@router.post("/", response_model=KnowledgeItemResponse)
async def create_knowledge_item(
    item: KnowledgeItemCreate,
    db: Session = Depends(get_db)
):
    db_item = KnowledgeItem(
        title=item.title,
        content=item.content,
        category=item.category,
        tags=item.tags,
        source=item.source,
        source_url=item.source_url
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.get("/", response_model=List[KnowledgeItemResponse])
async def list_knowledge_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = select(KnowledgeItem)
    
    if category:
        query = query.where(KnowledgeItem.category == category)
    
    if search:
        query = query.where(KnowledgeItem.content.ilike(f"%{search}%"))
    
    query = query.offset(skip).limit(limit).order_by(KnowledgeItem.created_at.desc())
    
    result = db.execute(query)
    items = result.scalars().all()
    return items


@router.get("/{item_id}", response_model=KnowledgeItemResponse)
async def get_knowledge_item(
    item_id: int,
    db: Session = Depends(get_db)
):
    result = db.execute(
        select(KnowledgeItem).where(KnowledgeItem.id == item_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Knowledge item not found")
    return item


@router.delete("/{item_id}")
async def delete_knowledge_item(
    item_id: int,
    db: Session = Depends(get_db)
):
    result = db.execute(
        select(KnowledgeItem).where(KnowledgeItem.id == item_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Knowledge item not found")
    
    db.delete(item)
    db.commit()
    return {"message": "Knowledge item deleted successfully"}


@router.get("/categories/list")
async def list_categories(db: Session = Depends(get_db)):
    result = db.execute(
        select(KnowledgeItem.category, func.count(KnowledgeItem.id))
        .where(KnowledgeItem.category.isnot(None))
        .group_by(KnowledgeItem.category)
    )
    categories = [{"name": row[0], "count": row[1]} for row in result.all()]
    return categories
