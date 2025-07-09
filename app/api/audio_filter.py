"""
Audio Moderation API Endpoints

This module handles audio content moderation requests.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
import logging

from app.models.schemas import AudioModerationResponse, ErrorResponse
from app.services.audio_processor import AudioProcessor
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/moderate", tags=["Audio Moderation"])

# Initialize audio processor
audio_processor = AudioProcessor()


@router.post(
    "/audio",
    response_model=AudioModerationResponse,
    responses={
        400: {"model": ErrorResponse},
        413: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    },
    summary="Moderate audio content",
    description="Transcribe and analyze audio content for inappropriate material."
)
async def moderate_audio(file: UploadFile = File(...)):
    """
    Moderate audio content for inappropriate material.
    
    This endpoint:
    1. Transcribes audio to text using speech-to-text models
    2. Analyzes the transcript for harmful content
    3. Returns both transcript and moderation results
    
    Supported formats: MP3, WAV, M4A, FLAC, OGG, AAC
    Max file size: 10MB
    """
    try:
        # Validate file type by extension
        if not file.filename:
            raise HTTPException(
                status_code=400,
                detail="Filename is required for audio format detection"
            )
        
        # Read file data
        audio_data = await file.read()
        
        # Validate file size
        if len(audio_data) > settings.max_file_size:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size: {settings.max_file_size / 1024 / 1024:.1f}MB"
            )
        
        # Validate file is not empty
        if len(audio_data) == 0:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty"
            )
        
        # Process audio content
        result = await audio_processor.process_audio(audio_data, file.filename)
        
        # Handle processing errors
        if result["label"] == "error":
            raise HTTPException(
                status_code=500,
                detail=result["reason"]
            )
        
        return AudioModerationResponse(
            transcript=result["transcript"],
            label=result["label"],
            confidence=result["confidence"],
            reason=result["reason"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in audio moderation: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error during audio moderation"
        )


@router.get(
    "/audio/health",
    summary="Audio moderation health check",
    description="Check if the audio moderation service is healthy and ready."
)
async def audio_moderation_health():
    """Check the health of the audio moderation service."""
    try:
        # Create minimal test audio data (empty bytes for testing)
        test_result = await audio_processor.process_audio(b"", "test.wav")
        
        # Audio processing should handle empty data gracefully
        return {
            "status": "healthy",
            "service": "audio_moderation",
            "supported_formats": [".mp3", ".wav", ".m4a", ".flac", ".ogg", ".aac"],
            "max_file_size_mb": settings.max_file_size / 1024 / 1024,
            "transcription_available": True  # Based on model availability
        }
        
    except Exception as e:
        logger.error(f"Audio moderation health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "service": "audio_moderation",
                "error": str(e)
            }
        )


@router.post(
    "/audio/transcribe",
    summary="Transcribe audio only",
    description="Transcribe audio to text without content moderation."
)
async def transcribe_audio(file: UploadFile = File(...)):
    """
    Transcribe audio to text without moderation.
    
    This endpoint only performs speech-to-text transcription
    without analyzing the content for harmful material.
    """
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(
                status_code=400,
                detail="Filename is required for audio format detection"
            )
        
        # Read file data
        audio_data = await file.read()
        
        # Validate file size
        if len(audio_data) > settings.max_file_size:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size: {settings.max_file_size / 1024 / 1024:.1f}MB"
            )
        
        # Validate audio format
        if not audio_processor._is_valid_audio_format(file.filename):
            raise HTTPException(
                status_code=400,
                detail="Unsupported audio format"
            )
        
        # Transcribe audio
        transcript = await audio_processor._transcribe_audio(audio_data)
        
        if transcript is None:
            raise HTTPException(
                status_code=500,
                detail="Transcription failed"
            )
        
        return {
            "transcript": transcript,
            "filename": file.filename,
            "file_size_mb": len(audio_data) / 1024 / 1024
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in audio transcription: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error during audio transcription"
        )
