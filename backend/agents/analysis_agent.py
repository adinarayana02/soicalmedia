from typing import List, Dict, Any
from models.text_model import analyze_text

class AnalysisAgent:
    """Passes standardized textual content through huge ML text evaluators."""
    
    def process_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        results = []
        for text in texts:
            # Analyze each fragment individually for safety
            res = analyze_text(text)
            results.append(res)
        return results
