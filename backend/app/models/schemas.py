from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class AnalysisRequest(BaseModel):
    text: Optional[str] = None
    image_base64: Optional[str] = None
    context: Optional[str] = None
    session_id: Optional[str] = None


class IntentAnalysis(BaseModel):
    real_intent: str
    metaphors: List[str]
    emotional_state: str
    attitude: str
    potential_traps: List[str]


class ReplySuggestion(BaseModel):
    type: str
    content: str
    pros: List[str]
    cons: List[str]


class AnalysisResult(BaseModel):
    intent_analysis: IntentAnalysis
    reply_suggestions: List[ReplySuggestion]
    related_knowledge: List[str]
    model_used: str


class KnowledgeItemCreate(BaseModel):
    title: str
    content: str
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    source: Optional[str] = None
    source_url: Optional[str] = None


class KnowledgeItemResponse(BaseModel):
    id: int
    title: str
    content: str
    category: Optional[str]
    tags: Optional[List[str]]
    source: Optional[str]
    source_url: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class ModelConfigUpdate(BaseModel):
    provider: str
    model_name: Optional[str] = None
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    is_active: Optional[bool] = None


class ModelConfigResponse(BaseModel):
    id: int
    provider: str
    model_name: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
