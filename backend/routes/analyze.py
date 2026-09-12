from fastapi import APIRouter, UploadFile, File, Form, Depends
from sqlalchemy.orm import Session
from database.db import get_db
from database.models import AnalysisResult, Upload, Interaction
from routes.auth import get_current_user

from agents.data_agent import DataAgent
from agents.preprocessing_agent import PreprocessingAgent
from agents.multimodal_agent import MultimodalAgent
from agents.observer_agent import ObserverAgent
from agents.evaluator_agent import EvaluatorAgent
from agents.advisor_agent import AdvisorAgent
from datetime import datetime
import json

router = APIRouter()

data_agent = DataAgent()
prep_agent = PreprocessingAgent()
mm_agent = MultimodalAgent()
observer_agent = ObserverAgent()
evaluator_agent = EvaluatorAgent()
advisor_agent = AdvisorAgent()

@router.post("/api/analyze")
async def analyze_single(
    text: str = Form(None), 
    file: UploadFile = File(None), 
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_user)
):
    """Handles text or singular media input."""
    file_bytes = await file.read() if file else None
    mime_type = file.content_type if file else None
    
    # Store upload record
    if file:
        new_upload = Upload(user_id=current_user.id, file_name=file.filename, upload_type="media")
        db.add(new_upload)
    
    payload = data_agent.process({"text": text, "file_bytes": file_bytes, "file_type": mime_type})
    media_text = mm_agent.process(payload["media_bytes"], payload["media_type"])
    
    combined_texts = []
    if payload["raw_text"]: combined_texts.append(payload["raw_text"])
    if media_text: combined_texts.append(media_text)
        
    cleaned_texts = prep_agent.process(combined_texts)
    if not cleaned_texts:
        return {"error": "No analyzable text found."}
        
    timeline_events = []
    for txt in cleaned_texts:
         timeline_events.append({
              "text": txt,
              "timestamp": datetime.utcnow(),
              "type": "message",
              "source": "manual_upload"
         })
         
    observed_events = observer_agent.process_timeline(timeline_events)
    eval_metrics = evaluator_agent.evaluate_session(observed_events)
    final_decision = advisor_agent.generate_advice(eval_metrics)
    
    summary_data = {
        "total_comments": 0,
        "total_likes": 0,
        "total_posts": len(cleaned_texts)
    }
    
    for txt in cleaned_texts:
        db.add(
            Interaction(
                user_id=current_user.id,
                engagement_type="comment",
                text_content=txt,
            )
        )
        
    # Save Results
    result_record = AnalysisResult(
        user_id=current_user.id,
        wellbeing_score=final_decision.get("wellbeing_score", 0),
        risk_level=final_decision.get("risk_level", "low"),
        behavioral_instability=eval_metrics.get("behavioral_instability", 0.0),
        temporal_risk_index=eval_metrics.get("temporal_risk_index", 0.0),
        distress_probability=eval_metrics.get("distress_probability", 0.0),
        sentiment="neutral",
        emotions=[],
        summary=summary_data,
        insights=final_decision.get("insights", "{}"),
        recommendations=final_decision.get("recommendations", ""),
        evidence=final_decision.get("evidence", ""),
        confidence=final_decision.get("confidence", 1.0)
    )
    db.add(result_record)
    db.commit()
    
    return {
        "summary": summary_data,
        "liked_posts": [],
        "comments": [{"text": t, "inference": inf.get("ml_results", {})} for t, inf in zip(cleaned_texts, observed_events)],
        "analysis": {
            "wellbeing_score": final_decision.get("wellbeing_score", 0),
            "risk_level": final_decision.get("risk_level", "low"),
            "behavioral_instability": eval_metrics.get("behavioral_instability", 0.0),
            "temporal_risk_index": eval_metrics.get("temporal_risk_index", 0.0),
            "distress_probability": eval_metrics.get("distress_probability", 0.0),
            "insights": json.loads(final_decision.get("insights", "{}")),
            "recommendations": final_decision.get("recommendations", ""),
            "evidence": final_decision.get("evidence", ""),
            "confidence": final_decision.get("confidence", 1.0)
        }
    }
