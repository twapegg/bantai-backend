from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.moderation_service import ImageModerationService
from app.config import settings

router = APIRouter(prefix="/moderation", tags=["Image Moderation"])
image_moderation_service = ImageModerationService(api_key=settings.openai_api_key)

class ImageModerationRequest(BaseModel):
    image_url: str

@router.get("/health")
async def image_moderation_health():
    """Health check for Image Moderation service."""
    if image_moderation_service.api_key:
        return {"status": "healthy"}
    return {"status": "unhealthy", "reason": "Missing OpenAI API key"}

@router.post("/image")
async def moderate_image(request: ImageModerationRequest):
    """Moderate an image using OpenAI omni-moderation-latest model."""
    result = await image_moderation_service.moderate_image_url(request.image_url)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result
