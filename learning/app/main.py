from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.database import SessionLocal, get_db
from app.models import LearningTask, LearningKeyword
from app.tasks.video_tasks import process_video_task, search_and_download_task, scheduled_learning
from app.tasks.knowledge_tasks import get_learning_statistics

app = FastAPI(title="Learning Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class LearningTaskCreate(BaseModel):
    platform: str
    url: str
    keyword: Optional[str] = None


class LearningTaskResponse(BaseModel):
    id: int
    platform: str
    keyword: Optional[str]
    video_id: Optional[str]
    video_url: Optional[str]
    video_title: Optional[str]
    video_author: Optional[str]
    status: str
    error_message: Optional[str]
    knowledge_extracted: bool
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class KeywordCreate(BaseModel):
    platform: str
    keyword: str


class KeywordResponse(BaseModel):
    id: int
    platform: str
    keyword: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "learning"}


@app.post("/tasks/", response_model=dict)
async def create_learning_task(task: LearningTaskCreate, db: Session = Depends(get_db)):
    db_task = LearningTask(
        platform=task.platform,
        keyword=task.keyword,
        video_url=task.url,
        status="pending"
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    celery_task = process_video_task.delay(db_task.id, task.platform, task.url)
    
    return {
        "task_id": db_task.id,
        "celery_task_id": celery_task.id,
        "status": "created"
    }


@app.get("/tasks/", response_model=List[LearningTaskResponse])
async def list_learning_tasks(
    skip: int = 0,
    limit: int = 20,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(LearningTask)
    
    if status:
        query = query.filter(LearningTask.status == status)
    
    tasks = query.order_by(LearningTask.created_at.desc()).offset(skip).limit(limit).all()
    return tasks


@app.get("/tasks/{task_id}", response_model=LearningTaskResponse)
async def get_learning_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(LearningTask).filter(LearningTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.post("/search/")
async def search_and_learn(
    platform: str,
    keyword: str,
    max_results: int = 5
):
    result = search_and_download_task.delay(platform, keyword, max_results)
    return {
        "status": "started",
        "celery_task_id": result.id,
        "platform": platform,
        "keyword": keyword
    }


@app.post("/keywords/", response_model=KeywordResponse)
async def create_keyword(keyword: KeywordCreate, db: Session = Depends(get_db)):
    existing = db.query(LearningKeyword).filter(
        LearningKeyword.platform == keyword.platform,
        LearningKeyword.keyword == keyword.keyword
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Keyword already exists")
    
    db_keyword = LearningKeyword(platform=keyword.platform, keyword=keyword.keyword)
    db.add(db_keyword)
    db.commit()
    db.refresh(db_keyword)
    return db_keyword


@app.get("/keywords/", response_model=List[KeywordResponse])
async def list_keywords(
    platform: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(LearningKeyword)
    
    if platform:
        query = query.filter(LearningKeyword.platform == platform)
    
    return query.all()


@app.delete("/keywords/{keyword_id}")
async def delete_keyword(keyword_id: int, db: Session = Depends(get_db)):
    keyword = db.query(LearningKeyword).filter(LearningKeyword.id == keyword_id).first()
    if not keyword:
        raise HTTPException(status_code=404, detail="Keyword not found")
    
    keyword.is_active = False
    db.commit()
    return {"message": "Keyword deactivated"}


@app.post("/trigger-scheduled/")
async def trigger_scheduled_learning():
    result = scheduled_learning.delay()
    return {
        "status": "triggered",
        "celery_task_id": result.id
    }


@app.get("/statistics/")
async def statistics():
    result = get_learning_statistics.delay()
    stats = result.get(timeout=30)
    return stats


@app.get("/statistics/summary")
async def statistics_summary(db: Session = Depends(get_db)):
    total = db.query(LearningTask).count()
    completed = db.query(LearningTask).filter(LearningTask.status == "completed").count()
    failed = db.query(LearningTask).filter(LearningTask.status == "failed").count()
    pending = db.query(LearningTask).filter(LearningTask.status == "pending").count()
    processing = db.query(LearningTask).filter(
        LearningTask.status.in_(["downloading", "transcribing", "extracting_knowledge"])
    ).count()
    
    return {
        "total": total,
        "completed": completed,
        "failed": failed,
        "pending": pending,
        "processing": processing,
        "success_rate": completed / total if total > 0 else 0
    }
