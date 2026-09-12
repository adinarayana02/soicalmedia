from typing import List, Dict, Any
from datetime import datetime
from models.text_model import analyze_text

class ObserverAgent:
    """
    Perception Layer:
    Extracts multimodal signals from the timeline.
    Outputs: S_i (Sentiment), T_i (Temporal), E_i (Engagement), C_i (Content Toxicity/Emotion), B_i (Behavioral Drift)
    """

    def _calculate_temporal_risk(self, timestamp: datetime) -> float:
        """
        Calculates T_i based on time of day. Late night (1AM - 5AM) = High risk.
        Normalized to 0.0 - 1.0
        """
        hour = timestamp.hour
        if 1 <= hour <= 5:
            return 1.0
        elif hour == 0 or hour == 6:
            return 0.5
        return 0.1 # Baseline normal activity

    def _calculate_engagement_level(self, event_type: str, text: str) -> float:
        """
        Calculates E_i.
        Messages/Comments = high engagement (conflict/emotion proxy).
        Likes/Saves = medium engagement.
        """
        e_type = event_type.lower()
        if "message" in e_type or "comment" in e_type:
            return 0.8 + (min(len(str(text)), 100) / 100.0) * 0.2
        if "like" in e_type or "saved" in e_type:
            return 0.4
        if "url" in e_type or "reel" in e_type:
            return 0.6
        return 0.5

    def process_timeline(self, timeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Processes a chronological timeline of events.
        timeline event: {"text": str, "timestamp": datetime, "type": str, "source": str}
        """
        observed_events = []
        
        # Sort timeline chronologically to ensure accurate B_i (drift) calculation
        timeline.sort(key=lambda x: x["timestamp"])
        
        prev_s_score = 0.5 # Neutral baseline for drift calculation

        for event in timeline:
            text = event.get("text", "")
            timestamp = event.get("timestamp", datetime.utcnow())
            event_type = event.get("type", "unknown")

            # 1. Base Sentiment & Emotion Analysis (ML)
            # Analyze each text snippet using the deep learning text models
            ml_results = analyze_text(text) if text else {"sentiment": "neutral", "emotions": []}
            
            # Convert string sentiment to numerical S_i score (0=Negative, 0.5=Neutral, 1=Positive)
            sentiment_map = {"positive": 1.0, "neutral": 0.5, "negative": 0.0}
            s_i = sentiment_map.get(ml_results.get("sentiment", "neutral"), 0.5)

            # 2. Extract Signals
            # L (Late-night activity)
            l_i = self._calculate_temporal_risk(timestamp)
            # E (Engagement)
            e_i = self._calculate_engagement_level(event_type, text)
            
            # Content Risk / Toxicity (T_i) natively from text_model if available
            t_i = ml_results.get("toxicity", 0.1)
            if "toxicity" not in ml_results:
                is_toxic_emotion = any(e in ["frustration", "anger"] for e in ml_results.get("emotions", []))
                t_i = 1.0 if (s_i < 0.3 and is_toxic_emotion) else 0.5 if s_i < 0.4 else 0.1
            
            # Behavioral Drift (B_i): Variance/change from previous state
            b_i = abs(prev_s_score - s_i)
            prev_s_score = s_i # Update state

            observed_events.append({
                "original_event": event,
                "ml_results": ml_results,
                "signals": {
                    "S": s_i,
                    "T": t_i,
                    "L": l_i,
                    "E": e_i,
                    "B": b_i
                }
            })
            
        return observed_events
