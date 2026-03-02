from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import analysis, knowledge, config, health, audio


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="AI驱动的社交智慧助手，帮助理解他人言语背后的真实意图",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router, prefix="/api", tags=["health"])
    app.include_router(analysis.router, prefix="/api/analysis", tags=["analysis"])
    app.include_router(knowledge.router, prefix="/api/knowledge", tags=["knowledge"])
    app.include_router(config.router, prefix="/api/config", tags=["config"])
    app.include_router(audio.router, prefix="/api/audio", tags=["audio"])

    return app


app = create_app()
