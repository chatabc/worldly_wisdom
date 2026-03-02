from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON
from sqlalchemy.sql import func
from app.services.database import Base


class KnowledgeItem(Base):
    __tablename__ = "knowledge_items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String(100))
    tags = Column(Text)
    source = Column(String(255))
    source_url = Column(String(1000))
    embedding_id = Column(String(255))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class ModelConfig(Base):
    __tablename__ = "model_configs"

    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String(50), unique=True, nullable=False)
    model_name = Column(String(100), nullable=False)
    api_key = Column(String(255))
    api_base = Column(String(255))
    is_active = Column(Boolean, default=False)
    config = Column(JSON)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class ConversationHistory(Base):
    __tablename__ = "conversation_history"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), index=True)
    user_input = Column(Text, nullable=False)
    analysis_result = Column(JSON)
    model_used = Column(String(100))
    created_at = Column(DateTime, server_default=func.now())


class LearningTask(Base):
    __tablename__ = "learning_tasks"

    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String(50), nullable=False)
    keyword = Column(String(255), nullable=False)
    video_id = Column(String(255))
    video_url = Column(String(1000))
    video_title = Column(String(500))
    status = Column(String(50), default="pending")
    error_message = Column(Text)
    extracted_text = Column(Text)
    knowledge_extracted = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime)
