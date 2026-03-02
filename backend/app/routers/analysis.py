from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
import json
from app.models.schemas import AnalysisRequest, AnalysisResult, IntentAnalysis, ReplySuggestion
from app.services.database import get_db
from app.services.llm_service import get_llm_service
from app.services.prompts import ANALYSIS_SYSTEM_PROMPT, REPLY_SUGGESTION_PROMPT
from app.config import settings

router = APIRouter()


@router.post("/analyze", response_model=AnalysisResult)
async def analyze_conversation(
    request: AnalysisRequest,
    db: Session = Depends(get_db)
):
    llm = get_llm_service()
    
    try:
        if request.image_base64:
            raw_response = await llm.analyze_image(
                image_base64=request.image_base64,
                text=request.text,
                system_prompt=ANALYSIS_SYSTEM_PROMPT
            )
        else:
            if not request.text:
                raise HTTPException(status_code=400, detail="Either text or image is required")
            raw_response = await llm.analyze_text(
                text=request.text,
                system_prompt=ANALYSIS_SYSTEM_PROMPT
            )
        
        try:
            intent_data = json.loads(raw_response)
            intent_analysis = IntentAnalysis(
                real_intent=intent_data.get("real_intent", ""),
                metaphors=intent_data.get("metaphors", []),
                emotional_state=intent_data.get("emotional_state", ""),
                attitude=intent_data.get("attitude", ""),
                potential_traps=intent_data.get("potential_traps", [])
            )
        except json.JSONDecodeError:
            intent_analysis = IntentAnalysis(
                real_intent=raw_response,
                metaphors=[],
                emotional_state="",
                attitude="",
                potential_traps=[]
            )
        
        reply_prompt = REPLY_SUGGESTION_PROMPT.format(
            conversation=request.text or "[图片对话]",
            analysis=json.dumps(intent_data if 'intent_data' in dir() else raw_response, ensure_ascii=False)
        )
        
        if request.text:
            reply_raw = await llm.analyze_text(
                text=request.text,
                system_prompt=reply_prompt
            )
        else:
            reply_raw = await llm.analyze_image(
                image_base64=request.image_base64,
                text="请根据分析结果提供回复建议",
                system_prompt=reply_prompt
            )
        
        try:
            reply_data = json.loads(reply_raw)
            suggestions = [
                ReplySuggestion(
                    type=s.get("type", ""),
                    content=s.get("content", ""),
                    pros=s.get("pros", []),
                    cons=s.get("cons", [])
                )
                for s in reply_data.get("suggestions", [])
            ]
        except json.JSONDecodeError:
            suggestions = []
        
        return AnalysisResult(
            intent_analysis=intent_analysis,
            reply_suggestions=suggestions,
            related_knowledge=[],
            model_used=settings.DEFAULT_MODEL_PROVIDER
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze/text")
async def analyze_text_only(text: str):
    llm = get_llm_service()
    response = await llm.analyze_text(text=text, system_prompt=ANALYSIS_SYSTEM_PROMPT)
    return {"analysis": response}
