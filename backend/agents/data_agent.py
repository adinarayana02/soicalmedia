from typing import Dict, Any

class DataAgent:
    """Handles raw input and categorizes it into a standard pipeline payload."""
    
    def process(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        payload example:
        {
           "text": "some raw text",
           "file_bytes": b"...",
           "file_type": "image/jpeg" 
        }
        """
        # Data standardization
        return {
            "raw_text": payload.get("text", ""),
            "media_bytes": payload.get("file_bytes", None),
            "media_type": payload.get("file_type", None),
            "source_type": "direct_input"
        }
