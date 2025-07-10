"""
Minimal Desktop Audio Transcription API

Simple endpoints for capturing and transcribing desktop audio via Stereo Mix.
"""

from fastapi import APIRouter, HTTPException
import logging
import threading
import pyaudio

from app.services.audio_processor import AudioProcessor

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/audio", tags=["Desktop Audio"])

# Single audio processor instance
audio_processor = AudioProcessor()


@router.get("/health")
async def health_check():
    """Check if Stereo Mix is available for desktop audio capture."""
    try:
        p = pyaudio.PyAudio()
        stereo_mix = audio_processor._find_stereo_mix(p)
        device_count = p.get_device_count()
        p.terminate()
        
        return {
            "status": "healthy",
            "stereo_mix_available": stereo_mix is not None,
            "total_devices": device_count
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

@router.post("/start")
async def start_transcription():
    """Start desktop audio transcription via Stereo Mix."""
    try:
        if audio_processor.is_streaming:
            return {"status": "already_running"}
        
        # Start transcription in background thread
        thread = threading.Thread(target=audio_processor.start_transcription)
        thread.daemon = True
        thread.start()
        
        return {"status": "started"}
        
    except Exception as e:
        logger.error(f"Failed to start transcription: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stop")
async def stop_transcription():
    """Stop desktop audio transcription."""
    try:
        audio_processor.stop_transcription()
        return {"status": "stopped"}
        
    except Exception as e:
        logger.error(f"Failed to stop transcription: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/transcript")
async def get_transcript():
    """Get latest transcript fragment and streaming status."""
    try:
        fragment = audio_processor.get_transcript()
        return {
            "fragment": fragment,
            "is_streaming": audio_processor.is_streaming
        }
        
    except Exception as e:
        logger.error(f"Failed to get transcript: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/devices")
async def list_devices():
    """Check Stereo Mix device availability."""
    try:
        p = pyaudio.PyAudio()
        stereo_mix = audio_processor._find_stereo_mix(p)
        device_count = p.get_device_count()
        p.terminate()
        
        return {
            "total_devices": device_count,
            "stereo_mix_available": stereo_mix is not None,
            "stereo_mix_device": stereo_mix
        }
        
    except Exception as e:
        logger.error(f"Failed to list devices: {e}")
        raise HTTPException(status_code=500, detail=str(e))
