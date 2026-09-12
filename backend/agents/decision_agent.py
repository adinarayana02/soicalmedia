from typing import Dict, Any

class DecisionAgent:
    """Final arbiter generating explainable AI insights based strictly on observable data without diagnosing."""
    
    def decide(self, aggregated: Dict[str, Any]) -> Dict[str, Any]:
        tally = aggregated.get("emotions_tally", {})
        sent_dist = aggregated.get("sentiment_distribution", {})
        dom_sent = aggregated.get("dominant_sentiment", "neutral")
        total = aggregated.get("total_items", 0)
        
        # Risk Evaluation
        neg_ratio = sent_dist.get('negative', 0) / max(total, 1)
        frustration = tally.get("frustration", 0) / max(total, 1)
        
        risk_level = "low"
        if neg_ratio > 0.4 or frustration > 0.3:
            risk_level = "medium"
        if neg_ratio > 0.6 and frustration > 0.5:
            risk_level = "high"
            
        # Insights String
        insights = []
        if dom_sent == "positive":
            insights.append("Your timeline demonstrates highly positive interactions.")
        elif dom_sent == "negative":
            insights.append("We observed a significant volume of negative sentiment in the sampled data.")
        else:
            insights.append("Overall sentiment is mostly neutral with occasional expressive bursts.")
            
        if "frustration" in tally and tally["frustration"] > 0:
             insights.append("Some interaction contexts indicate possible frustration or stress patterns.")
             
        # Recommendations
        recs = "Take breaks if you feel overwhelmed, and try engaging in positive spaces online."
        if risk_level == "high":
             recs = "Consider taking a digital detox this weekend. Seek offline engagements that bring you joy."
             
        return {
            "risk_level": risk_level,
            "insights": " ".join(insights),
            "recommendations": recs,
            "analysis": aggregated
        }
