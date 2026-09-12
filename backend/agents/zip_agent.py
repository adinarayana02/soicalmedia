import os
from zip_processor.extractor import process_social_zip
from typing import Dict, Any

class ZipDataAgent:
    """Handles the heavy structural extraction of ZIP exports into flat lists."""
    
    def process_zip(self, zip_filepath: str) -> Dict[str, Any]:
        """Delegates safe extraction and applies logical mapping."""
        if not os.path.exists(zip_filepath):
            raise FileNotFoundError(f"ZIP not found: {zip_filepath}")
            
        return process_social_zip(zip_filepath)
