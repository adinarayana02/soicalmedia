import json
from typing import Dict, Any

class AdvisorAgent:
    """
    Decision Layer (Explainable AI):
    Generates explainable outputs (Insights, Recommendations, Explanations, Confidence).
    MANDATORY output format: Reason, Evidence, Confidence.
    """
    
    def generate_advice(self, eval_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Takes inputs from EvaluatorAgent processing.
        Returns final package for DB storage / Dashboard UI.
        """
        
        # Unpack metrics
        wb = eval_metrics.get("wellbeing_score", 100.0)
        risk = eval_metrics.get("risk_score", 0.0)
        distress = eval_metrics.get("distress_probability", 0.0)
        instability = eval_metrics.get("behavioral_instability", 0.0)
        temporal = eval_metrics.get("temporal_risk_index", 0.0)
        sbc = eval_metrics.get("sudden_behavioral_change", 0)
        n_events = eval_metrics.get("events_evaluated", 0)
        
        # 1. Determine Risk Level & Score Alignment
        risk_score = round(risk, 2)
        if risk_score >= 60.0 or distress >= 0.75:
            risk_level = "High"
            if risk_score < 60.0:
                risk_score = round(max(60.0, distress * 100.0), 2)
            wb = max(0.0, round(100.0 - risk_score, 2))
        elif risk_score >= 30.0 or distress >= 0.45 or instability >= 0.45:
            risk_level = "Moderate"
            if risk_score < 30.0:
                risk_score = round(max(30.0, distress * 60.0), 2)
            wb = max(0.0, round(100.0 - risk_score, 2))
        else:
            risk_level = "Low"
            if risk_score >= 30.0:
                risk_score = round(min(29.9, risk_score), 2)
            wb = max(0.0, round(100.0 - risk_score, 2))
            
        # 2. Build Evidence

        top_contributors = []
        if temporal > 0.3:
            top_contributors.append("- High late-night usage")
        if distress > 0.5:
            top_contributors.append("- Indicators of distress detected")
        if instability > 0.4:
            top_contributors.append("- High behavioral drift/emotional variance")
        if sbc == 1:
            top_contributors.append("- Sudden worsening behavior detected")
            
        evidence = "\n".join(top_contributors) if top_contributors else "- Stable baseline interactions."
        
        # 3. Build Reason
        if risk_level == "High":
            reason = "Combination of negative signals (e.g., distress, volatility, late-night activity) critically increases behavioral risk."
            recs = "Please consider an immediate digital detox. It appears social media usage is currently impacting your wellbeing heavily."
        elif risk_level == "Moderate":
            reason = "Elevated temporal risk or mild distress indicators suggest potential strain."
            recs = "Monitor your late-night usage and try prioritizing positive engagements."
        else:
            reason = "Behavioral signals remain within healthy bounds with normal activity hours and stable emotional expression."
            recs = "Keep up your healthy digital habits."
            
        # 4. Confidence Score (Proxy based on data density)
        # More events = higher confidence. 
        confidence = min(1.0, 0.4 + (n_events / 100.0) * 0.6)
        
        insights_json = {
             "reasoning": reason,
             "evidence": evidence,
             "confidence_score": round(confidence, 2),
             "behavioral_instability": instability,
             "temporal_risk_index": temporal,
             "distress_probability": distress,
             "risk_score": risk_score
        }
        
        return {
             "risk_level": risk_level,
             "risk_score": risk_score,
             "wellbeing_score": wb,
             "insights": json.dumps(insights_json),
             "recommendations": recs,
             "evidence": evidence,
             "confidence": round(confidence, 2)
        }
