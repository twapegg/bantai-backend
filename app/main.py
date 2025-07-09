"""
FastAPI Application Entry Point

AI Content Moderation API for Parental Control System
"""

import logging
import sys
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException

from app.config import settings
from app.models.schemas import HealthResponse, ErrorResponse
from app.api import text_filter, image_filter, audio_filter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ]
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown."""
    # Startup
    logger.info("Starting AI Content Moderation API...")
    logger.info(f"Environment: {'Development' if settings.debug else 'Production'}")
    
    # Initialize services here if needed
    # e.g., warm up models, connect to databases, etc.
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI Content Moderation API...")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    AI-powered content moderation API for parental control systems.
    
    This API provides endpoints for:
    - Text content moderation using LLM/AI models
    - Image classification and NSFW detection
    - Audio transcription and content analysis
    
    Designed for integration with desktop applications and browser extensions.
    """,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    debug=settings.debug
)

# Add CORS middleware for browser extension support
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "path": str(request.url)
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status_code": 500,
            "path": str(request.url)
        }
    )


# Health check endpoint
@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Check API health and status"
)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version=settings.app_version
    )


# API status endpoint
@app.get(
    "/",
    summary="API Information",
    description="Get basic API information"
)
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "description": "AI Content Moderation API",
        "docs_url": "/docs",
        "health_url": "/health",
        "endpoints": {
            "text_moderation": "/moderate/text",
            "image_moderation": "/moderate/image",
            "audio_moderation": "/moderate/audio"
        }
    }


# Include API routers
app.include_router(text_filter.router)
app.include_router(image_filter.router)
app.include_router(audio_filter.router)


# Additional middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests."""
    start_time = time.time()
    
    # Log request
    logger.info(f"Request: {request.method} {request.url}")
    
    # Process request
    response = await call_next(request)
    
    # Log response
    process_time = time.time() - start_time
    logger.info(f"Response: {response.status_code} - {process_time:.3f}s")
    
    return response


if __name__ == "__main__":
    import uvicorn
    import time
    
    logger.info(f"Starting server on {settings.host}:{settings.port}")
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )
