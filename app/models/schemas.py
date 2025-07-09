from datetime import datetime
from typing import Optional, Union
from pydantic import BaseModel, Field


class TextModerationRequest(BaseModel):
    """Request schema for text moderation."""
    text: str = Field(..., description="Text content to moderate", max_length=10000)


class ImageModerationRequest(BaseModel):
    """Request schema for image moderation (used for validation)."""
    pass  # File upload handled by FastAPI's UploadFile


class AudioModerationRequest(BaseModel):
    """Request schema for audio moderation (used for validation)."""
    pass  # File upload handled by FastAPI's UploadFile


class ModerationResponse(BaseModel):
    """Base response schema for moderation results."""
    label: str = Field(..., description="Moderation label")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    reason: Optional[str] = Field(None, description="Reason for the moderation decision")
    timestamp: datetime = Field(default_factory=datetime.now, description="Processing timestamp")


class TextModerationResponse(ModerationResponse):
    """Response schema for text moderation."""
    label: str = Field(..., description="Text moderation label: 'harmful' or 'safe'")
    
    class Config:
        json_schema_extra = {
            "example": {
                "label": "harmful",
                "confidence": 0.85,
                "reason": "Contains inappropriate language",
                "timestamp": "2024-01-01T12:00:00"
            }
        }


class ImageModerationResponse(ModerationResponse):
    """Response schema for image moderation."""
    label: str = Field(..., description="Image moderation label: 'nudity', 'violence', 'safe', etc.")
    
    class Config:
        json_schema_extra = {
            "example": {
                "label": "safe",
                "confidence": 0.92,
                "reason": "No inappropriate content detected",
                "timestamp": "2024-01-01T12:00:00"
            }
        }


class AudioModerationResponse(ModerationResponse):
    """Response schema for audio moderation."""
    transcript: str = Field(..., description="Transcribed text from audio")
    label: str = Field(..., description="Audio content moderation label")
    
    class Config:
        json_schema_extra = {
            "example": {
                "transcript": "This is a sample audio transcript",
                "label": "safe",
                "confidence": 0.78,
                "reason": "No inappropriate content in transcript",
                "timestamp": "2024-01-01T12:00:00"
            }
        }


class HealthResponse(BaseModel):
    """Health check response schema."""
    status: str = Field(..., description="API status")
    timestamp: datetime = Field(default_factory=datetime.now)
    version: str = Field(..., description="API version")


class ErrorResponse(BaseModel):
    """Error response schema."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    timestamp: datetime = Field(default_factory=datetime.now)
