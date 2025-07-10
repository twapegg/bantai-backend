"""
Audio Processing Service - Stereo Mix capture and transcription
"""
import logging
import assemblyai as aai
from assemblyai.streaming.v3 import StreamingClient, StreamingClientOptions, StreamingParameters, TurnEvent, StreamingEvents

logger = logging.getLogger(__name__)
ASSEMBLYAI_API_KEY = "8ae8f00f8c83438e9329402cbcbe139d"

class AudioProcessor:
    """Simple Stereo Mix audio transcription service."""
    
    def __init__(self):
        self.latest_fragment = ""
        self.last_transcript = ""
        self.is_streaming = False
        aai.settings.api_key = ASSEMBLYAI_API_KEY  
        
    def start_transcription(self):
        """Start real-time transcription from Stereo Mix."""
        if self.is_streaming:
            return
        
        self.latest_fragment = ""
        self.last_transcript = ""
        
        try:
            client = StreamingClient(StreamingClientOptions(api_key=ASSEMBLYAI_API_KEY))
            
            def on_turn(_, event: TurnEvent):
                if event.transcript:
                    self._update_transcript(event.transcript)
            
            client.on(StreamingEvents.Turn, on_turn)
            client.connect(StreamingParameters(sample_rate=16000, format_turns=True))
            
            self.is_streaming = True
            
            # Find and use Stereo Mix
            import pyaudio
            p = pyaudio.PyAudio()
            device = self._find_stereo_mix(p)
            
            if device:
                stream = p.open(
                    format=pyaudio.paInt16,
                    channels=1,
                    rate=16000,
                    input=True,
                    input_device_index=device["index"],
                    frames_per_buffer=1024
                )
                
                def audio_generator():
                    while self.is_streaming:
                        try:
                            yield stream.read(1024, exception_on_overflow=False)
                        except:
                            break
                
                client.stream(audio_generator())
                stream.close()
            
            p.terminate()
            
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
        finally:
            self.is_streaming = False
    
    def stop_transcription(self):
        """Stop transcription."""
        self.is_streaming = False
    
    def get_transcript(self):
        """Get latest fragment only."""
        return self.latest_fragment
    
    def _find_stereo_mix(self, p):
        """Find Stereo Mix device."""
        for i in range(p.get_device_count()):
            device = p.get_device_info_by_index(i)
            name = device.get("name", "").lower()
            channels = device.get("maxInputChannels", 0)
            
            if channels > 0 and "stereo mix" in name:
                return {"index": i, "name": device.get("name")}
        
        logger.error("Stereo Mix not found - enable it in Windows Sound settings")
        return None
    
    def _update_transcript(self, new_text):
        """Store only the latest fragment for frontend consumption."""
        if not new_text or new_text == self.last_transcript:
            return
            
        # Extract only new content if this is an incremental update
        if self.last_transcript and new_text.startswith(self.last_transcript):
            # Extract only the new part
            new_part = new_text[len(self.last_transcript):].strip()
            if new_part:
                self.latest_fragment = new_part
            else:
                return  # No new content
        else:
            # Completely new content
            self.latest_fragment = new_text
        
        self.last_transcript = new_text
        logger.info(f"New fragment: '{self.latest_fragment}'")


