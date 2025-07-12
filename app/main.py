from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api import audio_filter, ocr, moderation

app = FastAPI(title=settings.app_name, version=settings.app_version, debug=settings.debug)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(audio_filter.router)
app.include_router(ocr.router)
app.include_router(moderation.router)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": settings.app_version}

@app.get("/")
async def root():
    return {"name": settings.app_name, "version": settings.app_version, "docs_url": "/docs"}
