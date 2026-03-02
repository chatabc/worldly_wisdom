from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base


class LearningTask(Base):
    __tablename__ = "learning_tasks"

    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String(50), nullable=False)
    keyword = Column(String(255), nullable=False)
    video_id = Column(String(255))
    video_url = Column(String(1000))
    video_title = Column(String(500))
    video_author = Column(String(255))
    video_duration = Column(Integer)
    status = Column(String(50), default="pending")
    error_message = Column(Text)
    extracted_text = Column(Text)
    knowledge_extracted = Column(Boolean, default=False)
    celery_task_id = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))


class LearningKeyword(Base):
    __tablename__ = "learning_keywords"

    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String(50), nullable=False)
    keyword = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    last_used = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
