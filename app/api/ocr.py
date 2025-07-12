from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.ocr_service import OCRService
from app.services.openai_service import OpenAIService
from app.config import settings

router = APIRouter(prefix="/ocr", tags=["OCR"])
ocr_service = OCRService(api_key=settings.ocr_api_key)
openai_service = OpenAIService(api_key=settings.openai_api_key)

@router.get("/health")
async def ocr_health():
    """Health check for OCR service."""
    if ocr_service.api_key:
        return {"status": "healthy"}
    return {"status": "unhealthy", "reason": "Missing OCR API key"}

class OCRRequest(BaseModel):
    image_url: str

@router.post("/image-text")
async def ocr_image(request: OCRRequest):
    """OCR endpoint for extracting text from an image URL."""
    result = await ocr_service.ocr_image_url(request.image_url)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result

@router.post("/image-text/analyze")
async def ocr_image_analyze(request: OCRRequest):
    """OCR endpoint for extracting text from an image URL and analyzing it with OpenAI."""
    ocr_result = await ocr_service.ocr_image_url(request.image_url)
    if "error" in ocr_result:
        raise HTTPException(status_code=500, detail=ocr_result["error"])
    text = ocr_result.get("text", "")
    if not text:
        raise HTTPException(status_code=400, detail="No text found in image.")
    try:
        moderation = await openai_service.analyze_text(text)
        result = {"text": text}
        flagged = False
        active_categories = []
        category_scores = {}
        analysis = moderation.get("analysis", {})
        result["moderation_analysis"] = analysis
        results = analysis.get("results", [])
        if results and isinstance(results, list):
            first_result = results[0]
            flagged = first_result.get("flagged", False)
            categories = first_result.get("categories", {})
            category_scores = first_result.get("category_scores", {})
            active_categories = [k for k, v in categories.items() if v]
        if flagged:
            emotion = await openai_service.analyze_emotion(text, active_categories, category_scores)
            if emotion and "emotion_analysis" in emotion:
                result["emotion_analysis"] = emotion["emotion_analysis"]
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI analysis failed: {str(e)}")
