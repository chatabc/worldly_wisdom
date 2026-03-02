from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Social Wisdom Assistant"}


@router.get("/")
async def root():
    return {
        "message": "Welcome to Social Wisdom Assistant API",
        "docs": "/docs"
    }
