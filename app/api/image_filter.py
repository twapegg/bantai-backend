"""
Minimized Image Moderation API
"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
import logging

from app.models.schemas import ImageModerationResponse
from app.services.image_classifier import ImageClassifier

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/moderate", tags=["Image Moderation"])
image_classifier = ImageClassifier()


class DataURLRequest(BaseModel):
    data_url: str


@router.post("/image", response_model=ImageModerationResponse)
async def moderate_image(file: UploadFile = File(...)):
    """Moderate image content."""
    try:
        # Basic validation
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="Must be an image file")
        
        # Read and classify
        image_data = await file.read()
        if len(image_data) == 0:
            raise HTTPException(status_code=400, detail="Empty file")
            
        result = await image_classifier.classify_image(image_data)
        
        if result["label"] == "error":
            raise HTTPException(status_code=500, detail=result["reason"])
            
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Image moderation failed: {e}")
        raise HTTPException(status_code=500, detail="Moderation failed")


@router.post("/image-batch")
async def moderate_image_batch(urls: list[str]):
    """Moderate multiple image URLs."""
    try:
        results = []
        for url in urls[:10]:  # Limit to 10 images
            result = await image_classifier.classify_image_url(url)
            results.append({"url": url, **result})
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/data-url")
async def moderate_data_url(request: DataURLRequest):
    """Moderate image from data URL (browser extensions)."""
    try:
        result = await image_classifier.classify_data_url(request.data_url)
        if result["label"] == "error":
            raise HTTPException(status_code=500, detail=result["reason"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/data-url-batch")
async def moderate_data_url_batch(data_urls: list[str]):
    """Moderate multiple canvas/screenshot data URLs."""
    try:
        results = []
        for i, data_url in enumerate(data_urls[:10]):  # Limit to 10 canvas images
            result = await image_classifier.classify_data_url(data_url)
            results.append({"index": i, **result})
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

