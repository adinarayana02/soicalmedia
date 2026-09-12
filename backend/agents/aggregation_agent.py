from typing import List, Dict, Any
from collections import Counter

class AggregationAgent:
    """Takes independent ML inferences and calculates a unified mathematical perspective."""
    
    def aggregate(self, inferences: List[Dict[str, Any]], context: Dict[str, Any] | None = None) -> Dict[str, Any]:
        """
        Calculates sentiment distribution and emotional consensus across many inferences.
        """
        if context is None:
            context = {}
            
        if not inferences:
            result = {
                "dominant_sentiment": "neutral",
                "emotions_tally": {},
                "sentiment_distribution": {"positive": 0, "negative": 0, "neutral": 0},
                "total_items": 0
            }
            result.update(context)
            return result
            
        sentiments = [res.get("sentiment", "neutral") for res in inferences]
        sentiment_dist = dict(Counter(sentiments))
        
        all_emotions = []
        for res in inferences:
            all_emotions.extend(res.get("emotions", []))
            
        emotion_dist = dict(Counter(all_emotions))
        
        dominant_sentiment = max(sentiment_dist, key=lambda k: sentiment_dist.get(k, 0)) if sentiment_dist else "neutral"
        
        result = {
            "dominant_sentiment": dominant_sentiment,
            "emotions_tally": emotion_dist,
            "sentiment_distribution": sentiment_dist,
            "total_items": len(inferences)
        }
        result.update(context)
        return result
