"""
Image Moderation API Endpoints

This module handles image content moderation requests.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
import logging

from app.models.schemas import ImageModerationResponse, ErrorResponse
from app.services.image_classifier import ImageClassifier
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/moderate", tags=["Image Moderation"])

# Initialize image classifier
image_classifier = ImageClassifier()


@router.post(
    "/image",
    response_model=ImageModerationResponse,
    responses={
        400: {"model": ErrorResponse},
        413: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    },
    summary="Moderate image content",
    description="Analyze image content for inappropriate material using AI models."
)
async def moderate_image(file: UploadFile = File(...)):
    """
    Moderate image content for inappropriate material.
    
    This endpoint analyzes images using various AI models and returns:
    - Label: 'nudity', 'violence', 'safe', etc.
    - Confidence score (0.0 to 1.0)
    - Reason for the decision
    
    Supported formats: JPEG, PNG, GIF, WebP
    Max file size: 10MB
    """
    try:
        # Validate file type
        if file.content_type not in settings.allowed_image_types:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file.content_type}. "
                      f"Supported types: {', '.join(settings.allowed_image_types)}"
            )
        
        # Read file data
        image_data = await file.read()
        
        # Validate file size
        if len(image_data) > settings.max_file_size:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size: {settings.max_file_size / 1024 / 1024:.1f}MB"
            )
        
        # Validate file is not empty
        if len(image_data) == 0:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty"
            )
        
        # Classify image content
        result = await image_classifier.classify_image(image_data)
        
        # Handle classification errors
        if result["label"] == "error":
            raise HTTPException(
                status_code=500,
                detail=result["reason"]
            )
        
        # Apply confidence threshold
        if result["confidence"] < settings.image_confidence_threshold:
            result["label"] = "uncertain"
            result["reason"] = f"Low confidence ({result['confidence']:.2f}): {result['reason']}"
        
        return ImageModerationResponse(
            label=result["label"],
            confidence=result["confidence"],
            reason=result["reason"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in image moderation: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error during image moderation"
        )


@router.get(
    "/image/health",
    summary="Image moderation health check",
    description="Check if the image moderation service is healthy and ready."
)
async def image_moderation_health():
    """Check the health of the image moderation service."""
    try:
        # Create a simple test image (1x1 RGB pixel)
        from PIL import Image
        from io import BytesIO
        
        test_image = Image.new('RGB', (1, 1), color='white')
        test_buffer = BytesIO()
        test_image.save(test_buffer, format='PNG')
        test_data = test_buffer.getvalue()
        
        # Test classification
        test_result = await image_classifier.classify_image(test_data)
        
        if test_result["label"] == "error":
            return JSONResponse(
                status_code=503,
                content={
                    "status": "unhealthy",
                    "service": "image_moderation",
                    "error": test_result["reason"]
                }
            )
        
        return {
            "status": "healthy",
            "service": "image_moderation",
            "supported_formats": settings.allowed_image_types,
            "max_file_size_mb": settings.max_file_size / 1024 / 1024,
            "confidence_threshold": settings.image_confidence_threshold
        }
        
    except Exception as e:
        logger.error(f"Image moderation health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "service": "image_moderation",
                "error": str(e)
            }
        )


@router.post(
    "/image/batch",
    summary="Moderate multiple images",
    description="Analyze multiple images in a batch request."
)
async def moderate_image_batch(files: list[UploadFile] = File(...)):
    """
    Moderate multiple images in a batch.
    
    This endpoint allows processing multiple images at once.
    Each image is processed independently and results are returned as a list.
    """
    try:
        if len(files) > 10:  # Limit batch size
            raise HTTPException(
                status_code=400,
                detail="Batch size too large. Maximum 10 images per batch."
            )
        
        results = []
        
        for i, file in enumerate(files):
            try:
                # Validate file type
                if file.content_type not in settings.allowed_image_types:
                    results.append({
                        "index": i,
                        "filename": file.filename,
                        "error": f"Unsupported file type: {file.content_type}"
                    })
                    continue
                
                # Read and validate file
                image_data = await file.read()
                if len(image_data) > settings.max_file_size:
                    results.append({
                        "index": i,
                        "filename": file.filename,
                        "error": "File too large"
                    })
                    continue
                
                # Classify image
                result = await image_classifier.classify_image(image_data)
                results.append({
                    "index": i,
                    "filename": file.filename,
                    "label": result["label"],
                    "confidence": result["confidence"],
                    "reason": result["reason"]
                })
                
            except Exception as e:
                results.append({
                    "index": i,
                    "filename": file.filename,
                    "error": str(e)
                })
        
        return {"results": results}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in batch image moderation: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error during batch image moderation"
        )
