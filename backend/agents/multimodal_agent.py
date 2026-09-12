from typing import Dict, Any
from models.image_model import analyze_image
from models.audio_model import analyze_audio

class MultimodalAgent:
    """Detects non-text capabilities and bridges them to standard text."""
    
    def process(self, media_bytes: bytes, media_type: str) -> str:
        """Translates image/audio bytes into text based on mime structure."""
        if not media_bytes or not media_type:
            return ""
            
        if media_type.startswith("image/"):
            return analyze_image(media_bytes)
            
        if media_type.startswith("audio/") or media_type.startswith("video/"):
            # Rely on Whisper for Audio. (Basic extraction assumes bytes are readable by Whisper)
            return analyze_audio(media_bytes)

        return ""
