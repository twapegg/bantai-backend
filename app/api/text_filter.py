"""
Text Moderation API Endpoints

This module handles text content moderation requests.
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
import logging

from app.models.schemas import (
    TextModerationRequest, 
    TextModerationResponse, 
    ErrorResponse
)
from app.services.text_analyzer import TextAnalyzer
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/moderate", tags=["Text Moderation"])

# Initialize text analyzer
text_analyzer = TextAnalyzer()


@router.post(
    "/text",
    response_model=TextModerationResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    },
    summary="Moderate text content",
    description="Analyze text content for harmful or inappropriate material using AI models."
)
async def moderate_text(request: TextModerationRequest):
    """
    Moderate text content for harmful or inappropriate material.
    
    This endpoint analyzes text using various AI models and returns:
    - Label: 'harmful' or 'safe'
    - Confidence score (0.0 to 1.0)
    - Reason for the decision
    """
    try:
        # Validate input
        if not request.text.strip():
            raise HTTPException(
                status_code=400,
                detail="Text content cannot be empty"
            )
        
        # Analyze text content
        result = await text_analyzer.analyze_text(request.text)
        
        # Handle analysis errors
        if result["label"] == "error":
            raise HTTPException(
                status_code=500,
                detail=result["reason"]
            )
        
        # Apply confidence threshold
        if result["confidence"] < settings.text_confidence_threshold:
            result["label"] = "uncertain"
            result["reason"] = f"Low confidence ({result['confidence']:.2f}): {result['reason']}"
        
        return TextModerationResponse(
            label=result["label"],
            confidence=result["confidence"],
            reason=result["reason"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in text moderation: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error during text moderation"
        )


@router.get(
    "/text/health",
    summary="Text moderation health check",
    description="Check if the text moderation service is healthy and ready."
)
async def text_moderation_health():
    """Check the health of the text moderation service."""
    try:
        # Test with a simple text
        test_result = await text_analyzer.analyze_text("Hello world")
        
        if test_result["label"] == "error":
            return JSONResponse(
                status_code=503,
                content={
                    "status": "unhealthy",
                    "service": "text_moderation",
                    "error": test_result["reason"]
                }
            )
        
        return {
            "status": "healthy",
            "service": "text_moderation",
            "model_available": text_analyzer.openai_client is not None,
            "confidence_threshold": settings.text_confidence_threshold
        }
        
    except Exception as e:
        logger.error(f"Text moderation health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "service": "text_moderation",
                "error": str(e)
            }
        )
