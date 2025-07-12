from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.ocr_service import OCRService
import os

router = APIRouter(prefix="/ocr", tags=["OCR"])
ocr_service = OCRService(api_key=os.getenv("OCR_API_KEY", "K86800457588957"))

class OCRRequest(BaseModel):
    image_url: str

@router.post("/image")
async def ocr_image(request: OCRRequest):
    """OCR endpoint for extracting text from an image URL."""
    result = await ocr_service.ocr_image_url(request.image_url)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result
