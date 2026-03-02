from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List
from app.models.schemas import ModelConfigUpdate, ModelConfigResponse
from app.models.models import ModelConfig
from app.services.database import get_db

router = APIRouter()


@router.get("/", response_model=List[ModelConfigResponse])
async def list_model_configs(db: Session = Depends(get_db)):
    result = db.execute(select(ModelConfig))
    configs = result.scalars().all()
    return configs


@router.put("/{provider}")
async def update_model_config(
    provider: str,
    config: ModelConfigUpdate,
    db: Session = Depends(get_db)
):
    result = db.execute(
        select(ModelConfig).where(ModelConfig.provider == provider)
    )
    db_config = result.scalar_one_or_none()
    
    if not db_config:
        db_config = ModelConfig(
            provider=provider,
            model_name=config.model_name or "",
            api_key=config.api_key,
            api_base=config.api_base,
            is_active=config.is_active or False
        )
        db.add(db_config)
    else:
        if config.model_name is not None:
            db_config.model_name = config.model_name
        if config.api_key is not None:
            db_config.api_key = config.api_key
        if config.api_base is not None:
            db_config.api_base = config.api_base
        if config.is_active is not None:
            db_config.is_active = config.is_active
    
    db.commit()
    db.refresh(db_config)
    return {"message": "Model config updated successfully", "config": ModelConfigResponse.model_validate(db_config)}


@router.post("/{provider}/activate")
async def activate_model(
    provider: str,
    db: Session = Depends(get_db)
):
    result = db.execute(select(ModelConfig))
    configs = result.scalars().all()
    
    for cfg in configs:
        cfg.is_active = (cfg.provider == provider)
    
    db.commit()
    return {"message": f"Model {provider} activated successfully"}
